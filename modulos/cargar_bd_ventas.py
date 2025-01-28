'''
modulo para ingresar la información de ventas con sus marcaciones a la base de datos
y ejectuar algunas consultas para el calculo de pi
'''
import pandas as pd
from helpers.utils import engine, psql_insert_copy
from helpers.logging import get_my_logger
from helpers.utils import cargar_config
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
    
    def _calculo_ajuste_metas(self):
        objeto = ajustes_ventas()
