from helpers.utils import cargar_config

config = cargar_config()

ditio =  {elemento[0]: elemento[1] for elemento in config['columnas_ventas'].values()}

valores = [nombre[0] for nombre in config['columnas_ventas'].values()]

print(ditio)