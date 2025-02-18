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
    ARG: de inicio del constructor data frame
    return df
    '''
    def __imputaciones(self,df):
        '''
        Imputaciones y ajustes de las columnas grupo_clientes y estrato
        ARG: df con la venta consolidad
        '''
        
        # reemplazos de la columna estrato_original
        df['estrato']=df['estrato_original'].replace(config['estrato'])
        df['estrato'] = df['estrato'].fillna('Estrato Bajo')
        
        # reemplazos columna grupo_cliente 5
        df['cod_grupo_cliente_5'] = np.where(~df['cod_grupo_cliente_5_orig'].isin(['AB','AC']),'AA',df['cod_grupo_cliente_5_orig'])
        df['grupo_cliente_5'] = np.where(~df['grupo_cliente_5_orig'].isin(['Grande','Mediano']),'Pequeño',df['grupo_cliente_5_orig'])
        
        return df

    def _cruce_df_lectura_vistas(self,df_base,query_vista,uniones):
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
        #el primer paso es eliminar las tipologias originales pues estan cambian y se parte de lo que esta en los universos.
        ventas_indirecta = ventas_indirecta.drop(columns=['clave_tipologia','tipologia','oficina_ventas','cod_jefe_ventas'])
        query_activos = 'SELECT * FROM clientes_activos_indirecta'
        df_ind = self._cruce_df_lectura_vistas(ventas_indirecta,query_activos,['cliente_clave','clave_agente'])
        
        query_portafolio_mat = 'SELECT * FROM tabla_portafolio'
        df_ind = self._cruce_df_lectura_vistas(df_ind,query_portafolio_mat,'cod_material')

        query_oficina_agente = 'SELECT * FROM oficina_agentes'
        df_ind = self._cruce_df_lectura_vistas(df_ind,query_oficina_agente,'clave_agente')
        
        df_ind = df_ind.drop(columns='cod_vendedor',axis=1)
        
        ## este paso se instancia una clase para imputar a partir
        ## del material el portafolio y la fuerza el vendedor.
        imputa_vende = vend_ind.actualiza_vendedores(df_ind)
        def_imputada = imputa_vende.marcacion_vendedor()
        def_imputada = def_imputada.drop_duplicates(subset=['clave_agente','cliente_clave','cod_material','cod_portafolio'],
                                                                keep='first')
        def_imputada = def_imputada.drop(columns=['codigo_fuerza','cod_portafolio'])
        login.info('Ajustes de clientes activos de indirecta ')
        print(def_imputada['venta_cop'].sum())
        return def_imputada

    def ajustes_directa(self,ventas_directa):
        '''
        Metodo para realizar ajustes de las ventas de la directa
        arg: df_ventas_directa
        return df ajustado
        '''
        ventas_directa = reducir_uso_memoria(ventas_directa)
        query_activos = 'SELECT * FROM clientes_activos_dir'
        df_dir = self._cruce_df_lectura_vistas(ventas_directa,query_activos,'cliente_clave')
        login.info('Ajustes de clientes activos de directa ')
        print(df_dir['venta_cop'].sum())
        return df_dir

    def ajustes_completos(self,df_ventas_dir,df_ventas_indi):
        '''
        Metodo para realizar ajustes completos despues de ajustes inciales a las ventas por su modelo de atención
        ARG: df1, df2, data frames de la directa e indirecta
        RETURN df
        '''
        data_consolida = pd.concat([df_ventas_dir,df_ventas_indi])
        ## se hacen primeras imputaciones a las ventas:

        data_anadido = self.__imputaciones(data_consolida)
        
        ##query de vista con los transformados trae canal sub canal
               
        query_trans =  'SELECT * FROM vista_tipoligia'
        data_anadido=  self._cruce_df_lectura_vistas(data_anadido,query_trans,'clave_tipologia')
        
        #imputa si el cliente es socio o no
        query_socios = "SELECT * FROM public.clientes_socios"
        data_anadido = self._cruce_df_lectura_vistas(data_anadido,query_socios,
                                                      'cliente_clave')
        ## imputando portafolio de AU
        query_pi_au_td = "SELECT * FROM portafolio_au_td"
        data_anadido = self._cruce_df_lectura_vistas(data_anadido,query_pi_au_td,
                                                      uniones=['cod_material','oficina_ventas','clave_tipologia','cod_grupo_cliente_5','estrato'])
        query_pi_bn_ce = "SELECT * FROM portafolio_bn_ce"
        data_anadido = self._cruce_df_lectura_vistas(data_anadido,query_pi_bn_ce,
                                                      uniones=['cod_material','oficina_ventas','clave_tipologia'])
      
        
        data_anadido["aplica_pi"] = data_anadido["pi_au_td"].combine_first(data_anadido["pi_bn_ce"])
        data_anadido = data_anadido.drop(columns=['pi_au_td','pi_bn_ce'])
        data_anadido['mes_meta'] = config['mes_meta']

        print(data_anadido.info())
        #data_anadido.to_csv('prueba_imputa1.csv',index=False)
        return data_anadido
        

