'''
Modulo para realizar ajustes y actualizaciones de las ventas
'''
import os
from modulos.consolidar_ventas import funciones_ventas



def run():
    '''
    funcion general para ejecutar los diferentes calculos de actualización de las ventas.
    '''
    ruta = os.path.join(os.getcwd(),'ventas')
    objeto_ventas = funciones_ventas(ruta)
    ventas_directa = objeto_ventas.consolidar_ventas_dir()
    ventas_indirecta = objeto_ventas.consolidar_ventas_ind()

    return True


if __name__ == '__main__':
    run()
