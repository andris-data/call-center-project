-- Exercise 1: Total calls per client
SELECT client_code, COUNT(contact_id) AS total_calls
FROM contacts
GROUP BY client_code
ORDER BY total_calls DESC;

-- Exercise 2: Call types breakdown for top 5 clients
SELECT client_code, call_types, COUNT(contact_id) AS total_calls
FROM contacts
WHERE client_code IN (
    SELECT client_code
    FROM contacts
    GROUP BY client_code
    ORDER BY COUNT(contact_id) DESC
    LIMIT 5
)
GROUP BY client_code, call_types
ORDER BY client_code, total_calls DESC;

-- Exercise 3: Busiest hours of the day
SELECT
    call_hour,
    COUNT(contact_id) AS total_calls,
    ROUND(
        COUNT(contact_id) * 100.0 / (
            SELECT COUNT(contact_id) FROM contacts
        ), 1
    ) AS percentage
FROM contacts
GROUP BY call_hour
ORDER BY call_hour ASC;

-- Exercise 4: Calls over 30 minutes
SELECT
    agent_full_name,
    client_code,
    call_types,
    dispositions,
    ROUND(handle_time_s / 60.0, 1) AS handle_time_mins
FROM contacts
WHERE handle_time_s >= 1800
ORDER BY handle_time_mins DESC;

-- Exercise 5: Abandoned vs handled breakdown
SELECT
    is_abandoned,
    COUNT(contact_id) AS total_calls,
    ROUND(
        COUNT(contact_id) * 100.0 / (
            SELECT COUNT(contact_id) FROM contacts
        ), 1
    ) AS percentage
FROM contacts
GROUP BY is_abandoned
ORDER BY total_calls DESC;