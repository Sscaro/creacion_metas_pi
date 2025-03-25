import pandas as pd
import numpy as np
import os
from helpers.utils import cargar_config

config = cargar_config()
'''
Modulo exclusivo para generar archivo de promos

'''

def generar_archivo_promo(ruta_portafolio:str, ruta_promos:str,hojas:list): 

    '''
    funcion para generar archivo relancionando el material con su respectiva promo si le aplica
    arg: ruta_portafolio: str con ruta de archivo de portafolio
        ruta_promos: ruta de archivo con los codigos promocionales
        hojas:  lista: listado de hojas del archivo de ruta_portafolio
    
    '''
    archivo_promo = pd.read_excel(ruta_promos,usecols=['cod_promo','cod_material'],dtype=str) 
    archivo_promo = archivo_promo.drop_duplicates(keep='first') 
    portafolio = pd.read_excel(ruta_portafolio,sheet_name=hojas,dtype=str)
    
    #hojas = pd.ExcelFile(portafolio)      
    writer = pd.ExcelWriter('PortafolioInfaltablePromos.xlsx')
    
    for hoja in hojas:
        consolidado = portafolio[hoja]
        consolidado = pd.merge(consolidado,archivo_promo,  how = 'left', left_on="Material Impactos", right_on= "cod_material")         
        consolidado["Material Aj2"]= np.where(consolidado["cod_promo"].isna(),consolidado["Material Impactos"] ,consolidado["cod_promo"])                
        consolidado['Canal Transformado'].replace('Comercio Especializa','Comercio Especializado',inplace=True)
        consolidado.to_excel(writer, sheet_name=hoja, index=False)

    writer.close()
    return 

ruta_porta = os.path.join(os.getcwd(),'Insumos',config['listado_insumos'][3])
ruta_promos = os.path.join(os.getcwd(),'Insumos',config['listado_insumos'][5])
generar_archivo_promo(ruta_porta,ruta_promos,['Infaltable TD','Infaltable AU','Infaltable CE','Infaltable B'])
