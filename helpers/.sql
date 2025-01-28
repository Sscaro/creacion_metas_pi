/*
QUERYS PARA CREACIÓN DE VISTAS  (PARA CREARLAS EN CASO DE TENERLAS QUE CARGAR NUEVAMENTE)

 */
CREATE VIEW clientes_activos_indirecta AS  /* marcacion cliente activos Indirecta*/
	SELECT DISTINCT(cliente_clave), clave_agente, 'Activo' AS Estado 
	FROM public.universo_indirecta;


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
SELECT DISTINCT(material_meta), oficina_ventas, clave_tipologia, 
	CASE 	WHEN segmento_valor = 'Grande'  THEN 'AC'
			WHEN segmento_valor = 'Mediano' THEN 'AB'
			ELSE  'AA' END AS cod_grupo_cliente_5,
	estrato
	FROM public.tabla_portafolio_au_td 
	LEFT JOIN tabla_tipologias ON tabla_portafolio_au_td.tipologia = tabla_tipologias.tipologia
	WHERE excluir_metas = 'No';


CREATE VIEW portafolio_bn_ce as /*vista para crear tabla de pi bn ce */
SELECT DISTINCT(material_meta), oficina_ventas, tabla_portafolio_bn_ce.tipologia ,clave_tipologia  from public.tabla_portafolio_bn_ce 
	LEFT JOIN tabla_tipologias ON tabla_portafolio_bn_ce.tipologia = tabla_tipologias.tipologia
	WHERE excluir_metas = 'No';



SELECT  oficina_ventas, clave_tipologia, 
	CASE 	WHEN segmento_valor = 'Grande'  THEN 'AC'
			WHEN segmento_valor = 'Mediano' THEN 'AB'
			ELSE  'AA' END AS cod_grupo_cliente_5,estrato,
			count(DISTINCT(material_meta)) AS Num_pi_aplica	
	FROM public.tabla_portafolio_au_td 
	LEFT JOIN tabla_tipologias ON tabla_portafolio_au_td.tipologia = tabla_tipologias.tipologia
	WHERE excluir_metas = 'No'
	group by oficina_ventas, clave_tipologia, cod_grupo_cliente_5,estrato;
	

CREATE VIEW vista_tipoligia as
SELECT clave_tipologia, canal_trans, sub_canal_trans FROM public.tabla_tipologias
