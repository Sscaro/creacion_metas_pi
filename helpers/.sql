/*
QUERYS PARA CREACIÓN DE VISTAS  (PARA CREARLAS EN CASO DE TENERLAS QUE CARGAR NUEVAMENTE)

 */
CREATE VIEW calculo_conteo_conteo AS  /* marcacion cliente activos Indirecta*/
	SELECT marcacion_ventas.tipo_venta,
    marcacion_ventas.anio_mes,
        CASE
            WHEN marcacion_ventas.tipo_venta = 'Directa'::text THEN '-'::text
            ELSE marcacion_ventas.clave_agente
        END AS clave_agente,
        CASE
            WHEN marcacion_ventas.tipo_venta = 'Directa'::text THEN '-'::text
            ELSE marcacion_ventas.nombre_agente
        END AS nombre_agente,
    marcacion_ventas.oficina_ventas,
    marcacion_ventas.cliente_clave,
        CASE
            WHEN marcacion_ventas.tipo_venta = 'Directa'::text THEN marcacion_ventas.cliente_clave
            ELSE marcacion_ventas.cod_ecom
        END AS cod_cliente_ecom,
    marcacion_ventas.nombre_cliente,
    marcacion_ventas.canal_trans,
    marcacion_ventas.sub_canal_trans,
    marcacion_ventas.tipologia,
    marcacion_ventas.clave_tipologia,
    marcacion_ventas.estrato,
    marcacion_ventas.cod_grupo_cliente_5,
    marcacion_ventas.grupo_cliente_5,
    marcacion_ventas.cod_vendedor,
    marcacion_ventas.nombre_vendedor,
    marcacion_ventas.cod_jefe_ventas,
    nombres_jfvtas.nombre_jefe_ventas,
	clientes_socios.socio,
    sum(marcacion_ventas.venta_cop) AS ventas_totales,
    COALESCE(sum(marcacion_ventas.venta_cop::double precision * marcacion_ventas.aplica_pi), 0::double precision) AS ventas_pi,
    count(DISTINCT
        CASE
            WHEN marcacion_ventas.venta_cop > 0 THEN marcacion_ventas.cod_material
            ELSE NULL::text
        END) AS num_material_comprados,
    COALESCE(sum(
        CASE
            WHEN marcacion_ventas.venta_cop > 0 THEN marcacion_ventas.aplica_pi
            ELSE NULL::double precision
        END), 0::double precision) AS num_pi_comprados
   FROM marcacion_ventas
     LEFT JOIN nombres_jfvtas ON marcacion_ventas.cod_jefe_ventas = nombres_jfvtas.cod_jefe_ventas
	 LEFT JOIN clientes_socios ON clientes_socios.cliente_clave = marcacion_ventas.cliente_clave
	 
  WHERE (marcacion_ventas.canal_trans = ANY (ARRAY['Tradicional'::text, 'Autoservicios'::text, 'Bienestar'::text, 'Comercio Especializado'::text, 'Otros Canales'::text])) AND marcacion_ventas.tipologia <> 'Agente Comercial'::text AND marcacion_ventas.estado = 'Activo'::text AND marcacion_ventas.mes_meta = 'FEB 2025'::text
  GROUP BY marcacion_ventas.tipo_venta, marcacion_ventas.anio_mes, marcacion_ventas.clave_agente, marcacion_ventas.nombre_agente, marcacion_ventas.oficina_ventas, marcacion_ventas.cliente_clave, socio,(
        CASE
            WHEN marcacion_ventas.tipo_venta = 'Directa'::text THEN marcacion_ventas.cliente_clave
            ELSE marcacion_ventas.cod_ecom
        END), marcacion_ventas.nombre_cliente, marcacion_ventas.canal_trans, marcacion_ventas.sub_canal_trans, marcacion_ventas.clave_tipologia, marcacion_ventas.tipologia, marcacion_ventas.estrato, marcacion_ventas.cod_grupo_cliente_5, marcacion_ventas.grupo_cliente_5, marcacion_ventas.cod_vendedor, marcacion_ventas.nombre_vendedor, marcacion_ventas.cod_jefe_ventas, nombres_jfvtas.nombre_jefe_ventas;
--/TERMINA CONSULTA

CREATE VIEW nombres_jfvtas AS
select distinct(cod_jefe_ventas), nombre_jefe_ventas from public.universo_directa



CREATE VIEW oficina_agentes AS
SELECT distinct(clave_agente), oficina_ventas FROM universo_indirecta

/*
VISTA PARA RECOMENDADOS AU Y TD
 */

CREATE VIEW recomen_Au_td AS(
 SELECT DISTINCT tabla_portafolio_au_td.material_impactos AS material_cod,
    tabla_portafolio_au_td.oficina_ventas,
    tabla_tipologias.clave_tipologia,
	tabla_tipologias.clave_canal_trans,
	tabla_tipologias.clave_sub_canal_trans,
	tabla_tipologias.clave_segmento,
        CASE
            WHEN tabla_portafolio_au_td.segmento_valor = 'Grande'::text THEN 'AC'::text
            WHEN tabla_portafolio_au_td.segmento_valor = 'Mediano'::text THEN 'AB'::text
            ELSE 'AA'::text
        END AS cod_grupo_cliente_5,
    tabla_portafolio_au_td.estrato
   FROM tabla_portafolio_au_td
    LEFT JOIN tabla_tipologias ON tabla_portafolio_au_td.tipologia = tabla_tipologias.tipologia

/*
VISTA PARA RECOMENDADOS BN Y TCE
 */

CREATE VIEW recomen_bn_ce AS (
SELECT DISTINCT tabla_portafolio_bn_ce.material_impactos AS cod_material,
    tabla_portafolio_bn_ce.oficina_ventas,
    tabla_tipologias.clave_tipologia,
	tabla_tipologias.clave_canal_trans,
	tabla_tipologias.clave_sub_canal_trans,
	tabla_tipologias.clave_segmento
   FROM tabla_portafolio_bn_ce
     LEFT JOIN tabla_tipologias ON tabla_portafolio_bn_ce.tipologia = tabla_tipologias.tipologia
)