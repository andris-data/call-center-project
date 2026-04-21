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
