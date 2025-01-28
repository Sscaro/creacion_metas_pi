'''
Modulo para realizar ajustes y actualizaciones de las ventas
'''
import os
from modulos.consolidar_ventas import funciones_ventas
from modulos.ajustes_ventas import ajustes_ventas

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


    #ventas_ind_ajustadas.to_csv('prueba_imputa1.csv',index=False,sep=";")
    return True


if __name__ == '__main__':
    run()
