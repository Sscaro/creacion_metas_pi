# creacion_metas_pi
Proyecto para Creacion metas PI CN

Este proyecto consiste en el calculo de las metas para portafolio infaltable.

Insumos: # Actualizar cada vez que sea necesario
    Clientes_activos_Dir_Ind.xlsx -> información de clientes activos de la dir e ind
    PortafolioInfaltable.xlsx -> información de materiales PI
    driver_Fuerza_portafolio.xlsx -> información de las fuerzas y portafolio vendedor
    drivers_transformados.xlsx -> Transformados.
    MaestrasSocios.xlsm -> Maestra de clientes socios.

archivo config:
    archivo yml con las columnas y la estructura de cada uno de los insumos

activar proyecto:
    source /venv/Scripts/activate

instalar librerias
    pip install -r requirements.txt

ejecutar
    python -m modulos.actualiza_drivers

actualizar los driver:
    python -m modulos.actualiza_driver
