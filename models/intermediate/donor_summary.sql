SELECT accounts.id, accounts.name, donations.donor_level, SUM(donations.amount) AS total_amount
FROM {{ ref('stg_account') }} AS accounts
LEFT JOIN {{ ref('int_donations_flat') }} AS donations
ON accounts.id = donations.account_id
GROUP BY ALL
