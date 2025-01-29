/*
QUERYS PARA CREACIÓN DE VISTAS  (PARA CREARLAS EN CASO DE TENERLAS QUE CARGAR NUEVAMENTE)

 */
CREATE VIEW clientes_activos_indirecta AS  /* marcacion cliente activos Indirecta*/
	SELECT  DISTINCT(cliente_clave), clave_agente,tabla_tipologias.clave_tipologia,
	tabla_tipologias.tipologia,
	'Activo' AS Estado 
	FROM public.universo_indirecta
	JOIN tabla_tipologias
	ON universo_indirecta.tipologia = tabla_tipologias.tipologia;


CREATE VIEW clientes_activos_dir 
AS
SELECT DISTINCT cliente_clave,
'Activo' AS estado
FROM universo_directa
WHERE (bloque_pedido <> ALL (ARRAY['01'::text, '06'::text, '08'::text, '09'::text, '10'::text, '11'::text, '12'::text, '13'::text, '14'::text, '15'::text, '17'::text, '23'::text, '24'::text, '26'::text, '27'::text, '39'::text])) OR bloque_pedido IS NULL;


CREATE VIEW universo_ind_fuerza AS /*Creación de la fuerza por cod_vendedor, cod_crm y fuerza*/
	SELECT  DISTINCT(cliente_clave), clave_agente, cod_vendedor,
			SPLIT_PART(fuerza,' -',1) AS cod_fuerza 
	FROM  public.universo_indirecta;



CREATE VIEW portafolio_au_td AS /*creacion de tabla de portafolio au y td*/
SELECT DISTINCT(material_meta) AS cod_material, oficina_ventas, clave_tipologia, 
	CASE 	WHEN segmento_valor = 'Grande'  THEN 'AC'
			WHEN segmento_valor = 'Mediano' THEN 'AB'
			ELSE  'AA' END AS cod_grupo_cliente_5,
			estrato,
			1 AS pi_au_td
	FROM public.tabla_portafolio_au_td 
	LEFT JOIN tabla_tipologias ON tabla_portafolio_au_td.tipologia = tabla_tipologias.tipologia
	WHERE excluir_metas = 'No';



CREATE VIEW portafolio_bn_ce as /*vista para crear tabla de pi bn ce */
SELECT DISTINCT(material_meta) as cod_material , oficina_ventas, clave_tipologia,
	1 AS pi_bn_ce	
	from public.tabla_portafolio_bn_ce 
	LEFT JOIN tabla_tipologias ON tabla_portafolio_bn_ce.tipologia = tabla_tipologias.tipologia
	WHERE excluir_metas = 'No';
	

CREATE VIEW vista_tipoligia as
SELECT clave_tipologia, canal_trans, sub_canal_trans FROM public.tabla_tipologias;


CREATE VIEW vista_num_pi_aplica_au_td AS
SELECT  oficina_ventas, clave_tipologia, 
	CASE 	WHEN segmento_valor = 'Grande'  THEN 'AC'
			WHEN segmento_valor = 'Mediano' THEN 'AB'
			ELSE  'AA' END AS cod_grupo_cliente_5,
			estrato, count(DISTINCT(material_meta)) AS Num_pi_aplica
	FROM public.tabla_portafolio_au_td	
	LEFT JOIN tabla_tipologias ON tabla_portafolio_au_td.tipologia = tabla_tipologias.tipologia
	WHERE excluir_metas = 'No'
	GROUP BY oficina_ventas, clave_tipologia, cod_grupo_cliente_5,estrato;

CREATE VIEW vista_num_pi_aplica_ce_cn AS
SELECT  oficina_ventas, clave_tipologia,
		COUNT(DISTINCT(material_meta))  AS num_aplica_bn_ce	
	from public.tabla_portafolio_bn_ce 
	LEFT JOIN tabla_tipologias ON tabla_portafolio_bn_ce.tipologia = tabla_tipologias.tipologia
	WHERE excluir_metas = 'No'
	GROUP BY oficina_ventas, clave_tipologia;


--/CONSULTA  CONTEOS DE IMPACTOS 
SELECT tipo_venta, marcacion_ventas.oficina_ventas, 
	cliente_clave,canal_trans,
	sub_canal_trans, marcacion_ventas.tipologia,
	clave_tipologia, 	
	marcacion_ventas.estrato,
	cod_grupo_cliente_5,
	marcacion_ventas.grupo_cliente_5,

	cod_vendedor,nombre_vendedor,	
	CASE
	WHEN tipo_venta = 'Directa' then marcacion_ventas.cod_jefe_ventas ELSE clave_agente END AS cod_jefe_clave_agente,

	CASE	
	WHEN tipo_venta = 'Directa' then nombres_jfvtas.nombre_jefe_ventas ELSE nombre_agente END AS nombre_jefe_clave_agente,		
	anio_mes,		
	SUM(venta_cop) AS ventas_totales,
	
	COALESCE(SUM(venta_cop * aplica_pi),0)  as ventas_pi,	
	
	count(distinct
		CASE WHEN venta_cop >0 
		THEN (cod_material) END) AS Num_material_comprados,		
	
	COALESCE(sum(
	CASE WHEN  venta_cop >0 
	THEN (aplica_pi) END),0) AS Num_pi_comprados		 


FROM public.marcacion_ventas
	LEFT JOIN nombres_jfvtas ON marcacion_ventas.cod_jefe_ventas = nombres_jfvtas.cod_jefe_ventas	
	WHERE canal_trans in ('Tradicional','Autoservicios','Bienestar','Comercio Especializado','Otros Canales')	
		AND marcacion_ventas.tipologia <> 'Agente Comercial'
		AND marcacion_ventas.estado = 'Activo'	
		AND mes_meta = 'ENE 2025'		
				
	group by tipo_venta, marcacion_ventas.oficina_ventas ,cliente_clave,canal_trans,
	sub_canal_trans,clave_tipologia ,marcacion_ventas.tipologia, marcacion_ventas. estrato,cod_grupo_cliente_5,marcacion_ventas.grupo_cliente_5,
	cod_vendedor,nombre_vendedor,	
	cod_jefe_clave_agente,nombre_jefe_clave_agente,anio_mes

--/TERMINA CONSULTA


CREATE VIEW nombres_jfvtas AS
select distinct(cod_jefe_ventas), nombre_jefe_ventas from public.universo_directa