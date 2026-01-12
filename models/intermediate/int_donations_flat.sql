SELECT
  account_id,
  donor_level,
  amount,
  amount_seq
FROM
  {{ ref('stg_donations') }}
LEFT JOIN UNNEST(l5_amounts) AS amount
WITH
OFFSET
  AS amount_seq
