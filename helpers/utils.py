'''
Modulo con funciones auxiliares.
'''
import os
import numpy as np
import pandas as pd
import yaml
import sqlalchemy
import csv
from io import StringIO

config_bd= {   'DRIVER_NAME':'postgresql+psycopg2',
    'DB_USER_NAME':'postgres',
    'DB_PASSWORD': 'clave2020',
    'DB_HOST':'localhost',
    'DB_PORT':'5433',
    'DB_NAME':'Bd_PI_metas'}

params_conexion = {
    'drivername':config_bd['DRIVER_NAME'],
    'username': config_bd['DB_USER_NAME'],
    'password': config_bd['DB_PASSWORD'],
    'host': config_bd['DB_HOST'],
    'port': config_bd['DB_PORT'],
    'database': config_bd['DB_NAME']
}


url = sqlalchemy.URL.create(
    drivername=params_conexion['drivername'],
    username=params_conexion['username'],
    password=params_conexion['password'],
    host=params_conexion['host'],
    port=params_conexion['port'],
    database=params_conexion['database']
)

engine = sqlalchemy.create_engine(url)

# Metodo obtenido desde la documentacion de pandas para cargar datos de manera masiva
# a bases de datos que soportan la sentencia COPY FROM
# Alternative to_sql() *method* for DBs that support COPY FROM
def psql_insert_copy(table, conn, keys, data_iter):
    """
    Execute SQL statement inserting data

    Parameters
    ----------
    table : pandas.io.sql.SQLTable
    conn : sqlalchemy.engine.Engine or sqlalchemy.engine.Connection
    keys : list of str
        Column names
    data_iter : Iterable that iterates the values to be inserted
    """
    # gets a DBAPI connection that can provide a cursor
    dbapi_conn = conn.connection
    with dbapi_conn.cursor() as cur:
        s_buf = StringIO()
        writer = csv.writer(s_buf)
        writer.writerows(data_iter)
        s_buf.seek(0)

        columns = ', '.join(['"{}"'.format(k) for k in keys])
        if table.schema:
            table_name = '{}.{}'.format(table.schema, table.name)
        else:
            table_name = table.name

        sql = 'COPY {} ({}) FROM STDIN WITH CSV'.format(
            table_name, columns)
        cur.copy_expert(sql=sql, file=s_buf)

def validate_columns(file_path, column_list,nombre_hoja=1,tipado=str):
    """
    Valida si todas las columnas de la lista están presentes en el archivo Excel.
    Si alguna columna no está presente, genera un error. Si todas están, devuelve un DataFrame con esas columnas.
    
    :param file_path: Ruta al archivo de Excel.
    :param column_list: Lista de nombres de columnas esperadas.
    :return: DataFrame con las columnas especificadas en column_list.
    """
    df = pd.read_excel(file_path,sheet_name=nombre_hoja,dtype=tipado)
    excel_columns = df.columns.tolist()
    
    # Validar que todas las columnas de la lista estén en las columnas del Excel
    missing_columns = [col for col in column_list if col not in excel_columns]
    if missing_columns:
        return (
            f"Las siguientes columnas faltan en el archivo Excel: {missing_columns}"
        )
    #assert all(col in excel_columns for col in column_list), (
    #    f"Las siguientes columnas faltan en el archivo Excel: "
    #    f"{[col for col in column_list if col not in excel_columns]}"
    #)

    filtered_df = df[column_list]
    filtered_df = filtered_df.drop_duplicates(keep='first')
    return filtered_df

def cargar_config():
    """
    Carga el archivo de configuración (config.yml) en un objeto de Python.
    El archivo de configuración debe estar en la carpeta "Insumos" en el directorio de trabajo actual.
    Luego llama a la función menu() para mostrar el menú principal.
    return: None
    """
    ruta_config  = os.path.join(os.getcwd(),'Insumos', 'config.yml')
    with open(ruta_config, 'r',encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

def reducir_uso_memoria(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Iterar sobre todas las columnas de un dataframe y modificar su tipo de dato para
    reducir el uso de memoria

    Args:
        DataFrame: Dataframe para ajustar los tipos de datos

    Returns:
        Dataframe: Un Dataframe de pandas con los tipos de datos ajustados
    '''

    # mem_inicial = df.memory_usage().sum() / 1024**2
    # print('El uso de memoria del dataframe es {:.2f} MB'.format(mem_inicial))

    for col in df.columns:
        tipo_dato_col = df[col].dtype

        if str(tipo_dato_col) != 'object':
            c_min = df[col].min()
            c_max = df[col].max()
            if str(tipo_dato_col)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)
        else:
            df[col] = df[col].astype('category')

