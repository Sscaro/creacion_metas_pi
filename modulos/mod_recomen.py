# Modulo para cargar archivos de recomendaciones
import pandas as pd
import numpy as np
import pandas.io.sql as pds
import pyodbc
from helpers.logging import get_my_logger
from helpers.utils import cargar_config
from helpers.utils import engine


login = get_my_logger()
config = cargar_config()

def distr_port_all_year(item):    
    """ Función para asignar una semana del año a cada material del portafolio agrupados por negocio
    ARG item: 
    """       
    item['WEEK_REC']= np.linspace(1, len(item), num=len(item))               
    return item

class modelo_recomendacion:

    '''
    Modulo para actualizar el archivo de recomendacion enviado a servicios
    '''
    def __init__(self):
        self.direccion_servidor = 'ause1-dl013-rds-pedido-sugerido.c3wpmbuihsox.us-east-1.rds.amazonaws.com, 3407' 
        self.nombre_bd = 'DataServices'
        self.nombre_usuario = 'reader_dataservices'
        self.password = 'D4t4s3rv1c3#2020*!'

    
    def __query_material(self):
        '''
        Metodo para obtener el query de los materiales que administran desde servicios
        return: df: driver_material

        '''
        try:
            conexion = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + 
                                        self.direccion_servidor+';DATABASE='+self.nombre_bd+';UID='+self.nombre_usuario+';PWD=' + self.password)
            login.info(("\n"*2))
            login.info('conexión exitosa')

        except Exception as e:
            login.info(f'"Ocurrió un error al conectar a SQL Server: ", {e}')

        query_mat ='''select ID AS material_cod,
        PROD_SECTOR_ID AS Sector   
        from [DataServices].[dbo].[PRODUCT];'''
        driver_negocio = pds.read_sql(query_mat,conexion)
        conexion.close()
        return driver_negocio


    def __ejecutar_query(self,query):
        '''
        Metodo para conectarse a un servidor sql server y ejecutar un query
        ARG: query: str: query a ejecutar
        return: df
        '''
        with engine.begin() as conn:          
            df = pd.read_sql_query(query, conn)
        
        return df
    
    def ajustes_portafolio_au_td(self):
        """
        Metodo para para ajustar el portafolio de au y td
        retund df

        """
        query_portafolio_AU_TD = 'SELECT * FROM recomen_Au_td'        
        df_portafolio_AU_TD = self.__ejecutar_query(query_portafolio_AU_TD)
        driver_material = self.__query_material()
        #df_portafolio_BN_CE = self.__ejecutar_query(query_portafolio_BN_CE)
        cod_oficinas = config['codigos_oficinas']

        df_portafolio_AU_TD['oficina_ventas'] = df_portafolio_AU_TD['oficina_ventas'].replace(cod_oficinas)
        
        df_portafolio_AU_TD = pd.merge(df_portafolio_AU_TD,driver_material,
                                       how='left',on='material_cod')
     
        login.info("Ajustes de portafolio AU_TD realizados.")
        login.info("Dimensiones de la tabla ajustada: %s", df_portafolio_AU_TD.shape)
        df_portafolio_AU_TD.columns = config['nombres_mod_recom_AU_TD']
   
        return df_portafolio_AU_TD
    
    def ajustes_portafolio_bn_cd(self):
        """
        Metodo para ajustar el portafolio de  be y ce
        retund df

        """
        query_portafolio_bn_ce = 'SELECT * FROM recomen_bn_ce'        
        df_portafolio_bn_ce = self.__ejecutar_query(query_portafolio_bn_ce)
        driver_material = self.__query_material() 
        cod_oficinas = config['codigos_oficinas']
        df_portafolio_bn_ce['oficina_ventas'] = df_portafolio_bn_ce['oficina_ventas'].replace(cod_oficinas)
        df_portafolio_bn_ce = pd.merge(df_portafolio_bn_ce,driver_material,
                                       how='left',on='material_cod')
        login.info("Ajustes de portafolio BN_CE realizados.")
        login.info("Dimensiones de la tabla ajustada: %s", df_portafolio_bn_ce.shape)
        df_portafolio_bn_ce.columns = config['nombres_mod_recom_bn_ce']
        
        return df_portafolio_bn_ce
    
    def archivo_pedido_sugerido(self):
        '''
        Metodo para calular el archivo de pedido sugerido
        return df
        '''
        porta_au_td  = self.ajustes_portafolio_au_td()
        porta_bn_ce =  self.ajustes_portafolio_bn_cd()

        cols_gral= list(porta_au_td.columns)
        cols_gral.remove('PRODUCT_ID')   
        items_gral= [group for name, group in porta_au_td.groupby(by=cols_gral)]

        cols_com_esp= list(porta_bn_ce.columns)
        cols_com_esp.remove('PRODUCT_ID')   


        items_com_esp= [group for name, group in porta_bn_ce.groupby(by=cols_com_esp)]
        dfs = [distr_port_all_year(grupo) for grupo in items_gral]
        dfs1 = [distr_port_all_year(grupo) for grupo in items_com_esp]
        port_all_year_gral = pd.concat(dfs, ignore_index=True)
        port_all_year_com_esp = pd.concat(dfs1, ignore_index=True)

        portafolio_gral = pd.concat([ port_all_year_com_esp, 
        port_all_year_gral,
        #port_all_year_cafe
        ], axis=0)
        portafolio_gral['CUST_GROUP4']= np.nan
        portafolio_gral['MUNICIPALITY']= np.nan

        portafolio_gral= portafolio_gral[['SALES_OFFICE_ID','DIST_CHANNEL_TRANS','SUB_DIST_CHAN_TRANS','TIPOL_TRANS',
                'CUST_GROUP4','CUST_GROUP5','CUST_TYPE_ID','STRATUM_GROUPED','SECTOR_ID',
                'MUNICIPALITY','PRODUCT_ID','WEEK_REC']]
                
        portafolio_gral['WEEK_REC']= portafolio_gral['WEEK_REC'].astype('int')
        portafolio_gral['WEEK_REC']= portafolio_gral['WEEK_REC'].astype('str')
        portafolio_gral['SECTOR_ID']= portafolio_gral['SECTOR_ID'].astype('int')
        portafolio_gral['SECTOR_ID']= portafolio_gral['SECTOR_ID'].astype('str')

        return portafolio_gral


objeto = modelo_recomendacion()
data_recomendado = objeto.archivo_pedido_sugerido()
data_recomendado.to_csv('data_recomendado.csv',index=False)



