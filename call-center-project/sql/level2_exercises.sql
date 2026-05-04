-- Exercise 1: How many call came in per day?
SELECT date, count(contact_id) as total_calls,
sum(is_abandoned) as total_abandoned,
ROUND(sum(is_abandoned)  * 100.0 /count(contact_id), 1) as abandonment_rate
FROM contacts
GROUP BY date
ORDER BY date ASC

-- Exercise 2: Call volume and abandonment rate by week(strftime is used for the SQLite)

SELECT strftime('%Y-%W', date) as week,
	count(contact_id) as calls,
	sum(is_abandoned) as total_abandoned,
	round(sum(is_abandoned) * 100.0 / count(contact_id), 1) as abandonment_rate
FROM contacts
GROUP BY week
ORDER BY week ASC


-- Exercise 3: Call volume and abandonment rate by Client
SELECT
    client_code,
    COUNT(contact_id) AS total_calls,
    SUM(is_abandoned) AS total_abandoned,
    ROUND(SUM(is_abandoned) * 100.0 / COUNT(contact_id), 1) AS abandonment_rate
FROM contacts
GROUP BY client_code
HAVING COUNT(contact_id) > 1000
AND ROUND(SUM(is_abandoned) * 100.0 / COUNT(contact_id), 1) > 10
ORDER BY abandonment_rate DESC


