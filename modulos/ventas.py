'''
Modulo para realizar ajustes y actualizaciones de las ventas
'''
import os
from modulos.consolidar_ventas import funciones_ventas
from modulos.ajustes_ventas import ajustes_ventas
from modulos.cargar_bd_ventas import ingesta_ventas

def run():
    '''
    funcion general para ejecutar los diferentes calculos de actualización de las ventas.
    '''
    ruta = os.path.join(os.getcwd(),'ventas')
    objeto_ventas = funciones_ventas(ruta)
    
    ventas_directa = objeto_ventas.consolidar_ventas_dir()
    ventas_indirecta = objeto_ventas.consolidar_ventas_ind()
    
    # estanciando objeto para ajuste de ventas de la dir e ind
    objeto_ventas_ajuste = ajustes_ventas()
    
    ventas_dir_ajustadas = objeto_ventas_ajuste.ajustes_directa(ventas_directa)
    ventas_ind_ajustadas = objeto_ventas_ajuste.ajustes_indirecta(ventas_indirecta) 
    ventas_consoldida = objeto_ventas_ajuste.ajustes_completos(ventas_dir_ajustadas,ventas_ind_ajustadas)
    print(ventas_consoldida.isnull().sum())
    
    #ventas_consoldida = 1
    objeto_ingesta = ingesta_ventas(ventas_consoldida)
    
    objeto_ingesta.cargar_sql()  # cargar marcacion de cliente material en una tabla y cargar a una tabla en sql
    #objeto_ingesta.calculo_ajuste_metas() # ajustes de conteos para calculo meta.
    

    return True

if __name__ == '__main__':
    run()

