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

Nota Clientes bajo estos codigos de pedido no se tendran en cuenta para la meta:
    01	No Compra
    06	Por fallecimiento
    08	Otras Listas Control
    09	Lista Ctrol Corporat
    10	Cliente en plan de p
    11	Cliente en pre-jurid
    12	Cliente en proceso j
    13	Cliente Castigado CC
    14	Proveed Castigado CP
    15	Clientes en Ley 550
    17	Cerro el Negocio
    23	Lista Procuraduría
    24	Lista ONU
    26	Lista Estupefaciente
    27	Cli.entr.a Indirecta
    39	Cliente en Liquidaci

imputaciones de los clientes vendedor sin portafolio
    - se establece imputar con la moda aquellos vendedores que desde los universos no tienen portafolio
        regla: moda entre agente comercial y vendedor mayor número de clientes en las fuerza de esta llave.
        si aun continuan valores nulos se imputa con la fuerza generoca 208 MULTIMARCA MIXTO

