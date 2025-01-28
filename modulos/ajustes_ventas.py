'''
Modulo para ajustar las ventas antes de subirlas a la base de datos

'''

import pandas as pd
import numpy as np
from helpers.logging import get_my_logger
from helpers.utils import cargar_config
from helpers.utils import reducir_uso_memoria
from helpers.utils import engine
import modulos.imputacion_vend_ind as vend_ind


login = get_my_logger()
config = cargar_config()

class ajustes_ventas:

    '''
    clase donde se resumen todos los ajustes tanto de la directa como indirecta 
    paramtros de inicio del constructor data frame
    '''
    def __imputaciones(self,df):
        '''
        Imputaciones y ajustes de las columnas grupo_clientes y estrato
        
        '''
        # reemplazos de la columna estrato_original
        df['Estrato_ajustado']=df['estrato_original'].map(config['estrato'])
        df['Estrato_ajustado'] = df['Estrato_ajustado'].fillna('Estrato Bajo')
        
        # reemplazos columna grupo_cliente 5
        df['cod_grupo_cliente_5_ajus'] = np.where(~df['cod_grupo_cliente_5_orig'].isin(['AB','AC']),'AA',df['cod_grupo_cliente_5_ajus'])
        df['grupo_cliente_5_ajus'] = np.where(~df['grupo_cliente_5_orig'].isin(['Grande','Mediano']),'Pequeño',df['grupo_cliente_5_ajus'])
        
        return df

    def __cruce_df_lectura_vistas(self,df_base,query_vista,uniones):
        '''
        Metodo para realizar difernetes merges a partir de un data frame
        base y una data frame de una consulta a la bd en postgres
        ARG: df base
            query_vista :str consutla sql
            uniniones: list valores para realizar el merge.
        return df
        '''
        with engine.begin() as conn: # gestor de contextos de conexión a postgres
              # Reemplaza con el nombre de tu vista
            df_vista = pd.read_sql_query(query_vista, conn)       
            df_base = pd.merge(df_base,df_vista,
                                on= uniones,           
                                suffixes=('_orig','_ajus'),
                                how='left'
                                   )    
        return df_base
    
    def ajustes_indirecta(self,ventas_indirecta):
        '''
        Metodo para realizar ajustes de las ventas de la indirecta
        arg: df df_ventas_indirecta
        return df ajustado
        '''
        query_activos = 'SELECT * FROM clientes_activos_indirecta'
        df_ind = self.__cruce_df_lectura_vistas(ventas_indirecta,query_activos,['cliente_clave','clave_agente'])
        
        query_portafolio_mat = 'SELECT * FROM tabla_portafolio'
        df_ind = self.__cruce_df_lectura_vistas(df_ind,query_portafolio_mat,'cod_material')
        
        df_ind = df_ind.drop(columns='cod_vendedor',axis=1)
        
        ## este paso se instancia una clase para imputar a partir
        ## del material el portafolio y la fuerza el vendedor.
        imputa_vende = vend_ind.actualiza_vendedores(df_ind)
        def_imputada = imputa_vende.marcacion_vendedor()
        def_imputada.drop_duplicates(subset=['clave_agente','cliente_clave','cod_material','cod_portafolio'],
                                                                keep='first')
        def_imputada = def_imputada.drop(columns=['codigo_fuerza','cod_portafolio'])
        return def_imputada

    def ajustes_directa(self,ventas_directa):
        '''
        Metodo para realizar ajustes de las ventas de la directa
        arg: df_ventas_directa
        return df ajustado
        '''
        ventas_directa = reducir_uso_memoria(ventas_directa)
        query_activos = 'SELECT * FROM clientes_activos_dir'
        df_dir = self.__cruce_df_lectura_vistas(ventas_directa,query_activos,'cliente_clave')
        login.info('Ajustes de clientes activos de directa ')
        print(df_dir['venta_cop'].sum())
        return df_dir

    def ajustes_completos(self,df_ventas_dir,df_ventas_indi):
        '''
        Metodo para realizar ajustes completos despues de ajustes inciales a las ventas por su modelo de atención
        '''
        data_consolida = pd.concat([df_ventas_dir,df_ventas_indi],axis=1)

        
