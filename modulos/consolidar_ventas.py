'''
Modulo para descomprimir archivos en formato .zip
borra los archivos .zip que quedaron.
consilida las ventas que estan por semana agrupando y separando la directa de la indirecta

'''
import os
import zipfile
import pandas as pd
from helpers.logging import get_my_logger 
from helpers.utils import cargar_config
#from helpers.utils import reducir_uso_memoria
from helpers.utils import agrupar_dataframe

config = cargar_config()
login = get_my_logger()

## directorio Ventas
class funciones_ventas:

    '''
        Clase con algunas funciones para ajustar los archivos de ventas
    '''
    def __init__(self,ruta):
        '''
        modulo constrctor
        arg: ruta: str : ruta de la carepta de ventas
        '''
        self.ruta = ruta

    def __descomprimir(self):       
        '''
        Metodo para descomprimir los archivos de ventas
        '''
        archivos = os.listdir(self.ruta)
        for archivo in archivos:
            if archivo.endswith('.zip'):
                nueva_carpeta = os.path.splitext(archivo)[0] # separa la extensión de achivo
                ruta_zip = os.path.join(self.ruta, archivo) # crea una carpeta con el nombre de la descargar
                directorio_destino = os.path.join(self.ruta, nueva_carpeta)
                os.makedirs(directorio_destino, exist_ok=True)
                        # Extraer el contenido del archivo ZIP
                with zipfile.ZipFile(ruta_zip, 'r') as zip_ref:
                    zip_ref.extractall(directorio_destino)
                
                for root, dirs, files in os.walk(directorio_destino):
                    for file in files:
                        if file.endswith('.csv'):
                            # Crear la ruta completa del archivo CSV
                            ruta_csv = os.path.join(root, file)
                            
                            # Renombrar y mover el archivo CSV al directorio principal
                            nuevo_nombre_csv = os.path.join(self.ruta, f'{nueva_carpeta}.csv')
                            os.rename(ruta_csv, nuevo_nombre_csv)
                
                # Eliminar la carpeta extraída después de mover el archivo CSV      
                os.rmdir(directorio_destino)
                os.remove(os.path.join(os.getcwd(),'Ventas',archivo))
        return print("Termina proceso de descomprimir archivos")

    def __validacion(self,df, columna, agrupa):
        '''
        Metodo para validar la suma de alguna variable numerica de archivos consolilidados.   
        ARG: df: data frame
            columna: columa a realizar operacion suma
            agrupa: str: valor para realizar agrupación 
            valor: float: número que se le asocia a la agrupación 

        return : dict  
        '''
        suma_validacion = df[columna].sum()
        valor_agrupado = {agrupa:suma_validacion}
        return valor_agrupado

    def __consolidar_ventas(self,tipo_venta = 'dir'):
        '''
        funcion para concatenar las ventas de la directa.
        ARG: atencion: str recibe dir o ind por defecto esta parametrizado dir
        '''
        try:
            self.__descomprimir()
        except AssertionError:
            login.info('No hay archivos para descomprimir...')

        dataframes = []
        
        archivos_objetivo = [archivo for archivo in os.listdir(self.ruta) if tipo_venta in archivo.lower() and archivo.endswith(".csv")]
        
        # lista para cambiar el nombre de las columnas del df
        nombre_columnas = [nombre[0] for nombre in config['columnas_ventas'].values()]
        # diccionario para tipar las columnas de cada achivo de ventas.
        tipado_columnas = {elemento[0]: elemento[1] for elemento in config['columnas_ventas'].values()}

        for archivo in archivos_objetivo:
            try:
                df = pd.read_csv(os.path.join(self.ruta, archivo), header=0,sep =",",decimal="," ,thousands=".", names=nombre_columnas,dtype=tipado_columnas)
            except AssertionError:
                df = pd.read_csv(os.path.join(self.ruta, archivo), header=0,sep =",",decimal=",",thousands="." , names=nombre_columnas,dtype=tipado_columnas)
                login.info('Algunos archivos estan sepadados por ,')
            dataframes.append(df)
            login.info('se ha leido archivo {} '.format(archivo))
            validacion = self.__validacion(df,'venta_cop',archivo)
            login.info('resultado de la suma de las ventas es: {}'.format(validacion))

        df_concatenado = pd.concat(dataframes, ignore_index=True)
        # extrae solo las columnas categoricas
        df_concatenado = agrupar_dataframe(df_concatenado)

        return df_concatenado
    
    def consolidar_ventas_dir(self):
        '''
        Metodo para consolisar las ventas dela directa       
        '''
        ventas_dir = self.__consolidar_ventas(tipo_venta='dir')
        return ventas_dir

    def consolidar_ventas_ind(self):
        '''
        Metodo para consolisar las ventas dela directa       
        '''
        ventas_indir = self.__consolidar_ventas(tipo_venta='ind')
        return ventas_indir


    ## crea un data frame con dos columnas numericas aletorias
