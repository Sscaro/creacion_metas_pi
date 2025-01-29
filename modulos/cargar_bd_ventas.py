'''
modulo para ingresar la información de ventas con sus marcaciones a la base de datos
y ejectuar algunas consultas para el calculo de pi
'''
import pandas as pd
import numpy as np
from helpers.utils import engine, psql_insert_copy
from helpers.logging import get_my_logger
from helpers.utils import cargar_config, agrupar_dataframe, ajustes_clientes_num
from modulos.ajustes_ventas import ajustes_ventas

login = get_my_logger()
config= cargar_config()

class ingesta_ventas:
    '''
    clase para cargar ventas a postgres
    y consultas para calculo de las metas
    ARG: df df vetnas Consolidada
    '''

    def __init__(self, dfventas):
        self.dfventas = dfventas


    def cargar_sql(self):    
        '''
        Metodo para cargar un las ventas a una tabla a la base de datos de posgres
        '''
        try:
            with engine.begin() as conn:          
                self.dfventas.to_sql('marcacion_ventas', con=conn, index=False, if_exists='append',method=psql_insert_copy)
                login.info('Se agregó la venta en la tabla marcacion_ventas')
            return True
        except AssertionError:
            return False
    
    def calculo_ajuste_metas(self):
         query_calculo_pi= 'SELECT * FROM calculo_conteo_conteo'
         with engine.begin() as conn: # gestor de contextos de conexión a postgres
              # Reemplaza con el nombre de tu vista
            df_calulo_pi = pd.read_sql_query(query_calculo_pi, conn) 
            listacol = ['tipo_venta',
                        'oficina_ventas',
                        'cliente_clave',
                        'canal_trans',
                        'sub_canal_trans',
                        'tipologia',
                        'clave_tipologia',                   
                        'estrato',
                        'cod_grupo_cliente_5',
                        'grupo_cliente_5',
                        'cod_vendedor',
                        'nombre_vendedor',
                        'cod_jefe_clave_agente',                 
                        'nombre_jefe_clave_agente'
                        ]
            
            valores = ['ventas_totales','ventas_pi','num_material_comprados','num_pi_comprados']
            df_calulo_pi = df_calulo_pi.pivot(index=listacol,
                                              columns='anio_mes',
                                              values = valores ).reset_index()
            df_calulo_pi.columns.name = None
            df_calulo_pi.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] for col in df_calulo_pi.columns]
            df_calulo_pi = df_calulo_pi.fillna(0)
            ### funciones para imputar algunos valores en # y algunos Sin asginar
            df_calulo_pi = ajustes_clientes_num(df_calulo_pi,col1='cod_vendedor',col2='cliente_clave')
            df_calulo_pi = ajustes_clientes_num(df_calulo_pi,col1='nombre_vendedor',col2='cliente_clave',valor = 'Sin asignar')
            df_calulo_pi = ajustes_clientes_num(df_calulo_pi,col1='cod_jefe_clave_agente',col2='cliente_clave')
            df_calulo_pi = ajustes_clientes_num(df_calulo_pi,col1='nombre_jefe_clave_agente',col2='cliente_clave',valor = 'Sin Asignar')
            ## agrupa los resultados
            df_calulo_pi = agrupar_dataframe(df_calulo_pi)  

            ###cruces materiales que aplica por cliente
            cruces_sql = ajustes_ventas()
            query_au_td = 'SELECT * FROM vista_num_pi_aplica_au_td'
            df_calulo_pi = cruces_sql._cruce_df_lectura_vistas(df_calulo_pi,query_au_td,['oficina_ventas','clave_tipologia','cod_grupo_cliente_5','estrato'])
            
            query_ce_bn= 'SELECT * FROM vista_num_pi_aplica_ce_cn'            
            df_calulo_pi= cruces_sql._cruce_df_lectura_vistas(df_calulo_pi,query_ce_bn,
                                                                      ['oficina_ventas','clave_tipologia'])
            
            df_calulo_pi["num_ref_pi_aplica"]= df_calulo_pi["num_pi_aplica"].combine_first(df_calulo_pi["num_aplica_bn_ce"])
            df_calulo_pi = df_calulo_pi.dropna(subset=['num_ref_pi_aplica'])
            df_calulo_pi = df_calulo_pi.drop(columns=['num_pi_aplica','num_aplica_bn_ce'])
            print(df_calulo_pi.info())
            ## calculos para calcular los promedios entre los n meses que se utilicen para el calulo
            ## los variables estan juntass mes a mes. 
            valor_incial= 14 # num_columna donde empiezan variables numericas para realizar los promedios (en este momento hay 2 meses s
            valor_final = 15 # columna siguiente las columnas estan una junta a la otra

            lista_columnas_promedio  = ['prom_ventas_cop','prom_ventas_pi_cop','prom_mate_unic_compr','prom_num_mate_pi_compr']
            for nuevacol in lista_columnas_promedio:
                df_calulo_pi[nuevacol] = df_calulo_pi.iloc[:, [valor_incial, valor_final]].mean(axis=1).round(0).astype(int)
                valor_incial+=2 # las columnnas del mismo dato van juntas, se se implementa un tercer mes cambiar este numero por 3
                valor_final+=2 # las columnnas del mismo dato van juntas, se se implementa un tercer mes cambiar este numero por 3
            df_calulo_pi = df_calulo_pi[df_calulo_pi['prom_ventas_cop']>0]
            df_calulo_pi['porc_part_pi'] = np.where(df_calulo_pi['prom_mate_unic_compr'] == 0, 0, np.round(df_calulo_pi['prom_num_mate_pi_compr'] / df_calulo_pi['prom_mate_unic_compr'], 3))
            
            # calculando los % de crecimieneto parar la meta
            condiciones = [
                df_calulo_pi['porc_part_pi'] < 0.4,
            (df_calulo_pi['porc_part_pi'] >= 0.4) & (df_calulo_pi['porc_part_pi'] < 0.5),
            (df_calulo_pi['porc_part_pi'] >= 0.5) & (df_calulo_pi['porc_part_pi'] < 0.6)
            ]
            valores = [0.08, 0.07, 0.06]
            df_calulo_pi['porc_crecimiento'] = np.select(condiciones, valores, default=0.05)
            df_calulo_pi['ref_pi_incrementar'] = (df_calulo_pi['porc_crecimiento']*df_calulo_pi['prom_num_mate_pi_compr']).round(0).astype(int)
            df_calulo_pi['total_refe_mas_incremento'] = df_calulo_pi['ref_pi_incrementar']+df_calulo_pi['prom_num_mate_pi_compr']
            df_calulo_pi.to_csv('calculo_final1.csv',index=False)        
            login.info("proceso culminado con exito.")

            return True