SELECT 
    r.id,
    r.repo_id,
    r.ead_id,
    r.title,
    r.finding_aid_filing_title,
    r.repository_processing_note,
    ev5.value AS 'finding aid status',
    r.publish,
    ev1.value AS 'status',
    ev2.value AS 'priority',
    e.number,
    ev3.value AS 'extent type',
    e.container_summary,
    e.physical_details,
    e.dimensions,
    cm.processing_total_extent,
    ev4.value 'processing total extent type',
    (SELECT 
            GROUP_CONCAT(DISTINCT loc.floor
                    SEPARATOR ', ')
        FROM
            sub_container AS sc
                JOIN
            top_container_link_rlshp AS tclr ON tclr.sub_container_id = sc.id
                JOIN
            top_container AS tc ON tc.id = tclr.top_container_id
                JOIN
            top_container_housed_at_rlshp AS tchar ON tchar.top_container_id = tc.id
                JOIN
            instance ON instance.id = sc.instance_id
                JOIN
            archival_object AS ao ON ao.id = instance.archival_object_id
                JOIN
            location AS loc ON loc.id = tchar.location_id
        WHERE
            ao.root_record_id = r.id
        GROUP BY r.id) AS floor,
    (SELECT 
            GROUP_CONCAT(DISTINCT loc.building
                    SEPARATOR ', ')
        FROM
            sub_container AS sc
                JOIN
            top_container_link_rlshp AS tclr ON tclr.sub_container_id = sc.id
                JOIN
            top_container AS tc ON tc.id = tclr.top_container_id
                JOIN
            top_container_housed_at_rlshp AS tchar ON tchar.top_container_id = tc.id
                JOIN
            instance ON instance.id = sc.instance_id
                JOIN
            archival_object AS ao ON ao.id = instance.archival_object_id
                JOIN
            location AS loc ON loc.id = tchar.location_id
        WHERE
            ao.root_record_id = r.id
        GROUP BY r.id) AS building,
    (SELECT 
            GROUP_CONCAT(DISTINCT loc.room
                    SEPARATOR ', ')
        FROM
            sub_container AS sc
                JOIN
            top_container_link_rlshp AS tclr ON tclr.sub_container_id = sc.id
                JOIN
            top_container AS tc ON tc.id = tclr.top_container_id
                JOIN
            top_container_housed_at_rlshp AS tchar ON tchar.top_container_id = tc.id
                JOIN
            instance ON instance.id = sc.instance_id
                JOIN
            archival_object AS ao ON ao.id = instance.archival_object_id
                JOIN
            location AS loc ON loc.id = tchar.location_id
        WHERE
            ao.root_record_id = r.id
        GROUP BY r.id) AS room
FROM
    resource r
        LEFT JOIN
    collection_management cm ON cm.resource_id = r.id
        LEFT JOIN
    enumeration_value ev1 ON cm.processing_status_id = ev1.id
        LEFT JOIN
    enumeration_value ev2 ON cm.processing_priority_id = ev2.id
        LEFT JOIN
    extent e ON e.resource_id = r.id
        LEFT JOIN
    enumeration_value ev3 ON e.extent_type_id = ev3.id
        LEFT JOIN
    enumeration_value ev4 ON cm.processing_total_extent_type_id = ev4.id
        LEFT JOIN
    enumeration_value ev5 ON r.finding_aid_status_id = ev5.id
WHERE
    r.repo_id = 20