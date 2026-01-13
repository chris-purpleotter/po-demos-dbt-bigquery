{{
    config(
        materialized='incremental',
        unique_key='pk'
    )
}}

WITH base AS (
  SELECT
    CURRENT_TIMESTAMP() AS submitted_at,
    GENERATE_UUID() AS pk,
    CAST(FLOOR(RAND() * 100) + 1 AS INT64) AS fk,
    CAST(FLOOR(RAND() * 5) + 1 AS INT64) AS qty,
    FROM UNNEST(GENERATE_ARRAY(1, 100)) 
)

SELECT *
FROM base
{% if is_incremental() %}
WHERE submitted_at >= (SELECT MAX(submitted_at) FROM {{ this }})
{% endif %}
QUALIFY ROW_NUMBER() OVER(ORDER BY RAND()) <= (SELECT FLOOR(RAND() * 15) + 1)