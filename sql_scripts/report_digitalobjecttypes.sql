-- This query counts all the digital objects with digital object types per each repository. 
-- It also includes a count of all digital objects without a digital object type per repository.
-- Now with proper 0s, due to count of digital object ids, rather than rows

SELECT
	repo.name as repository, coalesce(ev.value, "NO TYPE") as digital_object_type, COUNT(dobj.id) as count
FROM
	digital_object AS dobj
LEFT JOIN
	enumeration_value AS ev
    ON
    ev.id = dobj.digital_object_type_id
RIGHT JOIN
	repository AS repo
    ON
    repo.id = dobj.repo_id
WHERE
	repo.name != 'Global repository'
GROUP BY
	ev.value, repo.name
ORDER BY
	repo.name ASC;