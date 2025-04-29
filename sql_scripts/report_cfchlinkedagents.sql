-- Retrieves all agent_persons that are linked to in the CFCH repository. Updating this script to another repository is possible by changing the ao.repo_id code to the desired repository.
-- This is a test commit
SELECT
    name_person.sort_name AS agent_name, name_person.agent_person_id AS agent_id, evname.value AS name_source, evrole.value AS role
FROM
    linked_agents_rlshp AS rel
    	JOIN
	archival_object AS ao ON ao.id = rel.archival_object_id
		LEFT JOIN
	resource ON resource.id = rel.resource_id
        LEFT JOIN
    name_person ON name_person.agent_person_id = rel.agent_person_id
		LEFT JOIN
    enumeration_value AS evname ON evname.id = name_person.source_id
		JOIN
	enumeration_value AS evrole ON evrole.id = rel.role_id
		JOIN
	agent_record_identifier AS recordid ON recordid.id = rel.role_id
WHERE
    ao.repo_id = 21
GROUP BY name_person.id

-- To get the above to work properly, you'll need to run this query before running the above: SET SESSION sql_mode=(SELECT REPLACE(@@sql_mode, 'ONLY_FULL_GROUP_BY', ''));