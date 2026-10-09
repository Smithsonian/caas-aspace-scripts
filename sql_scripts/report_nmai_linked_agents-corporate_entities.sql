-- This query gets all agent_corporate_entities linked to NMAI resources and archival objects that have record IDs
-- (authorities such as naf, viaf, wikidata) and that do not have record IDs. The original request for the script asks to
-- exclude agent_corporate_entities with wikidata record sources, and commented out is one way to do that
-- (via ev.value NOT IN ('wikidata'), but that method was returning results with agents with wikidata sources, so more
-- troubleshooting is needed.

SELECT DISTINCT
    CONCAT('/agents/corporate_entities/', ac.id) AS agent_uri,
--     np.sort_name,
    GROUP_CONCAT(DISTINCT ev.value) AS authorities
FROM
    agent_corporate_entity AS ac
        JOIN
    linked_agents_rlshp AS lar ON lar.agent_corporate_entity_id = ac.id
        LEFT JOIN
    agent_record_identifier AS ari ON ari.agent_corporate_entity_id = ac.id
        LEFT JOIN
    resource AS res ON res.id = lar.resource_id
        LEFT JOIN
    enumeration_value AS ev ON ev.id = ari.source_id
--         LEFT JOIN
--     name_corporate_entity AS nc ON nc.agent_corporate_entity_id = ac.id
WHERE
    res.repo_id = 12
--     AND
--     ev.value NOT IN ('wikidata')
GROUP BY agent_uri--  , nc.sort_name
UNION SELECT DISTINCT
    CONCAT('/agents/corporate_entities/', ac.id) AS agent_uri,
--     np.sort_name,
    GROUP_CONCAT(DISTINCT ev.value) AS authorities
FROM
    agent_corporate_entity AS ac
        JOIN
    linked_agents_rlshp AS lar ON lar.agent_corporate_entity_id = ac.id
        LEFT JOIN
    agent_record_identifier AS ari ON ari.agent_corporate_entity_id = ac.id
        LEFT JOIN
    archival_object AS ao ON ao.id = lar.archival_object_id
        LEFT JOIN
    enumeration_value AS ev ON ev.id = ari.source_id
--         LEFT JOIN
--     name_corporate_entity AS nc ON nc.agent_corporate_entity_id = ac.id
WHERE
    ao.repo_id = 12
--     AND
--     ev.value NOT IN ('wikidata')
GROUP BY agent_uri--  , nc.sort_name
UNION SELECT DISTINCT
    CONCAT('/agents/corporate_entities/', ac.id) AS agent_uri,
--     np.sort_name,
    NULL
FROM
    agent_corporate_entity AS ac
        JOIN
    linked_agents_rlshp AS lar ON lar.agent_corporate_entity_id = ac.id
        LEFT JOIN
    resource AS res ON res.id = lar.resource_id
--         LEFT JOIN
--     name_corporate_entity AS nc ON nc.agent_corporate_entity_id = ac.id
WHERE
    res.repo_id = 12
GROUP BY agent_uri--  , nc.sort_name
UNION SELECT DISTINCT
    CONCAT('/agents/corporate_entities/', ac.id) AS agent_uri,
--     np.sort_name,
    NULL
FROM
    agent_corporate_entity AS ac
        JOIN
    linked_agents_rlshp AS lar ON lar.agent_corporate_entity_id = ac.id
        LEFT JOIN
    archival_object AS ao ON ao.id = lar.archival_object_id
--         LEFT JOIN
--     name_corporate_entity AS nc ON nc.agent_corporate_entity_id = ac.id
WHERE
    ao.repo_id = 12
GROUP BY agent_uri--  , nc.sort_name