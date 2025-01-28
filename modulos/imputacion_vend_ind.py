'''
Modulo para imputar los vendedores de la indirecta con base en las fuerza y portafolio
'''
import pandas as pd
from helpers.utils import engine
from helpers.logging import get_my_logger
from helpers.utils import cargar_config


login = get_my_logger()
config = cargar_config()

class actualiza_vendedores:
    '''
    Metodo para actualizar los vendedores de la indirecta
    '''
    def __init__(self,df_ventas):
        '''
        df_ventas: df con las ventas de la indirecta con la maración del portafolio que le aplica al material
        '''
        self.df_ventas = df_ventas

    def __imputacion_fuerza_universo(self):
        '''        
        en los unviersos hay clientes que no tienen una fuerza asociada, por lo tanto
        se deben imputar con la moda del vendedor
        return df.
        '''
        with engine.begin() as conn:
            query_vista = 'SELECT * FROM public.universo_ind_fuerza'
            df_universo_indire = pd.read_sql_query(query_vista, conn)
            # En esta parte del codigo se extrae la moda de la fuerza a partir de llave Agente Vendedor
            moda_fuerza = (
                df_universo_indire.groupby(["clave_agente", "cod_vendedor"])["codigo_fuerza"]
                .agg(lambda x: x.mode().iloc[0] if not x.mode().empty else None)
                .reset_index()
                .rename(columns={"codigo_fuerza": "moda_cod_fuerza"})
            )
                
            df_universo_indire = pd.merge(df_universo_indire,moda_fuerza, on=["clave_agente", "cod_vendedor"], how="left")
            df_universo_indire["codigo_fuerza"] = df_universo_indire["codigo_fuerza"].fillna(df_universo_indire["moda_cod_fuerza"])
          
            df_universo_indire = df_universo_indire.drop(columns=["moda_cod_fuerza"])

            ## si aun continuan valores nulos en el codigo de fuerza se imputa con el cod 208 MULTIMARCA MIXTO         
            df_universo_indire['codigo_fuerza'] = df_universo_indire['codigo_fuerza'].fillna('208')    
            print('universo imputado')
           
        return df_universo_indire

    def __combina_cliente_fuerza_portafolio(self):
        '''
        este metodo consiste en crear una tabla a nivel de cliente, portafolio, fuerza
        para luego cruzarla con las ventas con la llave cliente - portafolio
        '''
        universo = self.__imputacion_fuerza_universo() 
        
        with engine.begin() as conn:
            query_portafolio = 'SELECT * FROM tabla_fuerza'
            df_fuerza_portafolio = pd.read_sql_query(query_portafolio, conn)             
            fuerza_portafolio = pd.merge(universo,df_fuerza_portafolio, on ='codigo_fuerza', how='left')
        return fuerza_portafolio
    
    def marcacion_vendedor(self):
        '''
        Metodo para extraer vendedor a partir de la clave cliente-portafolio
        returnd df
        '''
        fuerza_porta = self.__combina_cliente_fuerza_portafolio()
       
        resultado_ventas = pd.merge(self.df_ventas,fuerza_porta, on =['cliente_clave','clave_agente','cod_portafolio'],how='left') 
        return resultado_ventas
