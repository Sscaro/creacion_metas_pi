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



SELECT tipo_venta, oficina_ventas, 
	cod_vendedor,
	cliente_clave, 
	CASE
		WHEN tipo_venta = 'Directa' then cod_jefe_ventas ELSE clave_agente END AS cod_jefe_clave_agente,
	nombre_agente,
	anio_mes,
	SUM(venta_cop) AS ventas_totales,
	COALESCE(SUM(venta_cop * aplica_pi),0)  as ventas_pi,
	count(distinct(cod_material)) AS Num_material_comprados,
	COALESCE(sum(aplica_pi),0) AS Num_pi_comprados,
	COALESCE(sum(aplica_pi),0)/ NULLIF(count(distinct(cod_material)),0) AS Porc_pi_compr,
	CASE
		WHEN COALESCE(sum(aplica_pi),0)/ NULLIF(count(distinct(cod_material)),0) < 0.4 THEN 0.08
		WHEN COALESCE(sum(aplica_pi),0)/ NULLIF(count(distinct(cod_material)),0)  BETWEEN 0.4 AND 0.5 THEN 0.07
		WHEN COALESCE(sum(aplica_pi),0)/ NULLIF(count(distinct(cod_material)),0)  BETWEEN 0.5 AND 0.6 THEN 0.06
		ELSE 0.05 END AS porc_incremento	 
FROM public.marcacion_ventas
	WHERE canal_trans in ('Tradicional','Autoservicios','Bienestar','Comercio Especializa','Otros Canales')	
	AND tipologia <> 'Agente Comercial'
	AND estado = 'Activo'
group by tipo_venta, oficina_ventas ,cliente_clave, cod_vendedor ,cod_jefe_clave_agente,nombre_agente,anio_mes
