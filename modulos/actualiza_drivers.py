'''
modulo para atualizar driver en la bd
'''
import os
from helpers.logging import get_my_logger # Importa la función de logging.
from helpers.utils import cargar_config
from helpers.utils import validate_columns
from helpers.utils import engine


login = get_my_logger()
config = cargar_config()



class UpdateDriver:
    '''
    Clase para cargar cada insumo
    '''
    def __init__(self):  
        #self.config = cargar_config()       
        self.ruta = os.path.join(os.getcwd(), 'Insumos')

    def __leer_universos(self,valor_column,archivo,hoja=1):
        '''
        Metodo para actualizar universo de la directa
        arg: valor_column dict: nombre de las columnas y nombres nuevos de las columnas
            valor_lista: Int numero en la lista de lista_insumos
            valor_config: str: nombre del diccionario archivo connfig
        return df
        '''
        df = validate_columns(os.path.join(self.ruta, archivo) , valor_column.keys(),nombre_hoja=hoja)        
        df = df.rename(columns=valor_column)         
        
        return df
    
    
    def __load_to_sql(self, valor_column,archivo,table_name ,hoja=1,existe='replace'):
        '''
        Metodo para cargar un df a la base de datos de postgres
        '''
       
        with engine.begin() as conn:
            data = self.__leer_universos(valor_column,archivo,hoja=hoja)
            login.info('tamaño del archivo anexado: %s',data.shape)
            print(data.info())
            data.to_sql(table_name, con=conn, index=False, if_exists=existe)
            return True

    def cargar_directa(self):
        '''
        cargar universo de la directa a la bd
        '''
        result = self.__load_to_sql(config['columnas_universos_dir'],config['listado_insumos'][0],config['tablas_bd_pi_metas'][6],hoja='directa',existe='append')
        if result is True:
            return login.info(f"Actualización de la tabla {config['tablas_bd_pi_metas'][6]} exitosa")      
        else:
            return login.warning("Error al actualizar la tabla %s", config['tablas_bd_pi_metas'][6])


    def cargar_indirecta(self):
        '''
        cargar universo de la indirecta
        '''
        result = self.__load_to_sql(config['lista_universo_ind'],config['listado_insumos'][0],config['tablas_bd_pi_metas'][7],hoja='indirecta',existe='append')
        if result is True:
            return login.info(f"Actualización de la tabla {config['tablas_bd_pi_metas'][7]} exitosa")      
        else:
            return login.warning("Error al actualizar la tabla %s", config['tablas_bd_pi_metas'][7])


    def cargar_fuerza_vend(self):
        '''
        cargar a la bd driver de fuerza de vendedor
        '''
        result = self.__load_to_sql(config['driver_fuerza_portafolio']['driver_fuerza'],config['listado_insumos'][1],config['tablas_bd_pi_metas'][1],hoja='driver_fuerza',existe='append')
        if result is True:
            return login.info(f"Actualización de la tabla {config['tablas_bd_pi_metas'][1]} exitosa")      
        else:
            return login.warning("Error al actualizar la tabla %s", config['tablas_bd_pi_metas'][1])


    def cargar_portafolio_material(self):
        '''
        cargar a la bd driver de portafolio vendedor
        '''
        result = self.__load_to_sql(config['driver_fuerza_portafolio']['driver_portafolio'],config['listado_insumos'][1],config['tablas_bd_pi_metas'][2],hoja='driver_portafolio',existe='append')
        if result is True:
            return login.info(f"Actualización de la tabla {config['tablas_bd_pi_metas'][2]} exitosa")      
        else:
           return login.warning("Error al actualizar la tabla %s", config['tablas_bd_pi_metas'][2])

    
    def cargar_tipologia(self):
        '''
        cargar a la bd driver de portafolio vendedor
        '''
        result = self.__load_to_sql(config['driver_transformados']['tipologia'],config['listado_insumos'][2],config['tablas_bd_pi_metas'][5],hoja='tipologia',existe='append')
        if result is True:
            return login.info(f"Actualización de la tabla {config['tablas_bd_pi_metas'][5]} exitosa")      
        else:
           return login.warning("Error al actualizar la tabla %s", config['tablas_bd_pi_metas'][5]) 
    
    def cargar_pi_au_td(self):
        '''
        cargar a la base de datos la tabla de pi au td
        '''
        result = self.__load_to_sql(config['portafolio']['portafolio_au_td'],config['listado_insumos'][3],config['tablas_bd_pi_metas'][3],hoja='Infaltable TD',existe='append')
        result = self.__load_to_sql(config['portafolio']['portafolio_au_td'],config['listado_insumos'][3],config['tablas_bd_pi_metas'][3],hoja='Infaltable AU',existe='append')
        if result is True:
            return login.info(f"Actualización de la tabla {config['tablas_bd_pi_metas'][3]} exitosa")      
        else:
           return login.warning("Error al actualizar la tabla %s", config['tablas_bd_pi_metas'][3])   

    def cargar_pi_bn_ce(self):
        '''
        cargar a la base de datos la tabla de pi ce bi
        '''
        result = self.__load_to_sql(config['portafolio']['portafolio_bn_ce'],config['listado_insumos'][3],config['tablas_bd_pi_metas'][4],hoja='Infaltable CE',existe='append')
        result = self.__load_to_sql(config['portafolio']['portafolio_bn_ce'],config['listado_insumos'][3],config['tablas_bd_pi_metas'][4],hoja='Infaltable B',existe='append')
        if result is True:
            return login.info(f"Actualización de la tabla {config['tablas_bd_pi_metas'][4]} exitosa")      
        else:
           return login.warning("Error al actualizar la tabla %s", config['tablas_bd_pi_metas'][4])            


actualizacion = UpdateDriver()
#actualizacion.cargar_directa()
#actualizacion.cargar_indirecta()
actualizacion.cargar_fuerza_vend()
actualizacion.cargar_portafolio_material()
actualizacion.cargar_tipologia()
actualizacion.cargar_pi_au_td()
actualizacion.cargar_pi_bn_ce()
