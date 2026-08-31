SELECT 
    res.ead_id,
    res.title,
    CONCAT('repositories/',
            res.repo_id,
            '/resources/',
            res.id) AS resource_uri,
    CONVERT( JSON_EXTRACT(CAST(CONVERT( note.notes USING UTF8) AS CHAR (65000)),
            '$.subnotes[0].content') USING UTF8MB3) AS conditions_governing_access,
    NULL AS updated_accessrestrict_note
FROM
    note
        JOIN
    resource AS res ON note.resource_id = res.id
WHERE
    res.repo_id = 20
        AND note.notes LIKE '%accessrestrict%'
