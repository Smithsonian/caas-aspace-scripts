-- Search for all digital objects across all repositories (except test - 11, training - 23, NMAH-AF - 50, 
-- and CHSDM - 52) that contain linked_agents, dates (except dates with labels = 'digitized'), extents, 
-- lang_material, note (of any kind), and subjects
SELECT 
    digobj.id, digobj.digital_object_id, digobj.title
FROM
    digital_object AS digobj
        JOIN
    linked_agents_rlshp ON linked_agents_rlshp.digital_object_id = digobj.id
        JOIN
    date ON date.digital_object_id = digobj.id
        JOIN
    extent ON extent.digital_object_id = digobj.id
		JOIN
    lang_material ON lang_material.digital_object_id = digobj.id
        JOIN
    note ON note.digital_object_id = digobj.id
        JOIN
    subject_rlshp ON subject_rlshp.digital_object_id = digobj.id
WHERE
    lang_material.digital_object_id IS NOT NULL
        OR extent.digital_object_id IS NOT NULL
        OR linked_agents_rlshp.digital_object_id IS NOT NULL
        OR date.digital_object_id IS NOT NULL
        AND date.label_id != 2727
        OR note.digital_object_id IS NOT NULL
        OR subject_rlshp.digital_object_id IS NOT NULL
        AND digobj.repo_id NOT IN (11,23,50,52)
GROUP BY digobj.id
	