-- This query counts all the digital objects with digital object types per each repository. 
-- It also includes a count of all digital objects without a digital object type per repository.

SELECT
	repo.name as repository, ifnull(ev.value, "NO TYPE") as digital_object_type, COUNT(ifnull(ev.value, 1)) as count
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
GROUP BY
	ev.value, repo.name