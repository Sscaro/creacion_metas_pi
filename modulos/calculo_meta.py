'''
modulo para el calculo de la meta
'''
from modulos.cargar_bd_ventas import ingesta_ventas

ventas_consoldida = {}
objeto_ingesta = ingesta_ventas(ventas_consoldida)
objeto_ingesta.calculo_ajuste_metas()