# change the locationString as needed
set @locationString = 'NMAH, Basement, CB-023%';

    SELECT
        distinct ev.value,
        tc.indicator,
        tc.barcode,
        CONCAT('/repositories/',
        tc.repo_id,
        '/top_containers/',
        tc.id) as uri,
        resource.title,
        replace(replace(replace(replace(replace(resource.identifier,
        ',',
        '.'),
        '"',
        ''),
        ']',
        ''),
        '[',
        ''),
        '.null',
        '') as 'Resource Number',
        l.title,
        l.building,
        l.floor,
        l.room,
        l.area,
        l.coordinate_1_label,
        l.coordinate_1_indicator,
        l.coordinate_2_label,
        l.coordinate_2_indicator,
        l.coordinate_3_label,
        l.coordinate_3_indicator  
    FROM
        location l  
    LEFT JOIN
        top_container_housed_at_rlshp tcr 
            ON tcr.location_id = l.id 
    LEFT JOIN
        top_container tc 
            ON tc.id = tcr.top_container_id 
    LEFT JOIN
        top_container_link_rlshp tclr 
            ON tclr.top_container_id = tc.id 
    LEFT JOIN
        sub_container sc 
            ON tclr.sub_container_id = sc.id 
    JOIN
        instance i 
            ON i.id = sc.instance_id # also need to handle resource 
            and accession links 
    JOIN
        archival_object ao 
            ON ao.id = i.archival_object_id 
    JOIN
        resource 
            ON ao.root_record_id = resource.id 
    LEFT JOIN
        enumeration_value ev 
            ON tc.type_id = ev.id  
    WHERE
        l.title LIKE @locationString   
    
	UNION
    ALL SELECT
        distinct ev.value,
        tc.indicator,
        tc.barcode,
        CONCAT('/repositories/',
        tc.repo_id,
        '/top_containers/',
        tc.id) as uri,
        resource.title,
        replace(replace(replace(replace(replace(resource.identifier,
        ',',
        '.'),
        '"',
        ''),
        ']',
        ''),
        '[',
        ''),
        '.null',
        '') as 'Resource Number',
        l.title,
        l.building,
        l.floor,
        l.room,
        l.area,
        l.coordinate_1_label,
        l.coordinate_1_indicator,
        l.coordinate_2_label,
        l.coordinate_2_indicator,
        l.coordinate_3_label,
        l.coordinate_3_indicator   
    FROM
        location l  
    LEFT JOIN
        top_container_housed_at_rlshp tcr 
            ON tcr.location_id = l.id 
    LEFT JOIN
        top_container tc 
            ON tc.id = tcr.top_container_id 
    LEFT JOIN
        top_container_link_rlshp tclr 
            ON tclr.top_container_id = tc.id 
    LEFT JOIN
        sub_container sc 
            ON tclr.sub_container_id = sc.id 
    JOIN
        instance i 
            ON i.id = sc.instance_id # also need to handle resource 
            and accession links 
    JOIN
        resource 
            ON resource.id = i.resource_id 
    LEFT JOIN
        enumeration_value ev 
            ON tc.type_id = ev.id   
    WHERE
        l.title LIKE @locationString   
    
	UNION
    ALL SELECT
        distinct ev.value,
        tc.indicator,
        tc.barcode,
        CONCAT('/repositories/',
        tc.repo_id,
        '/top_containers/',
        tc.id) as uri,
        accession.title,
        replace(replace(replace(replace(replace(accession.identifier,
        ',',
        '.'),
        '"',
        ''),
        ']',
        ''),
        '[',
        ''),
        '.null',
        '') as 'Resource Number',
        l.title,
        l.building,
        l.floor,
        l.room,
        l.area,
        l.coordinate_1_label,
        l.coordinate_1_indicator,
        l.coordinate_2_label,
        l.coordinate_2_indicator,
        l.coordinate_3_label,
        l.coordinate_3_indicator   
    FROM
        location l  
    LEFT JOIN
        top_container_housed_at_rlshp tcr 
            ON tcr.location_id = l.id 
    LEFT JOIN
        top_container tc 
            ON tc.id = tcr.top_container_id 
    LEFT JOIN
        top_container_link_rlshp tclr 
            ON tclr.top_container_id = tc.id 
    LEFT JOIN
        sub_container sc 
            ON tclr.sub_container_id = sc.id 
    JOIN
        instance i 
            ON i.id = sc.instance_id # also need to handle resource 
            and accession links 
    JOIN
        accession 
            ON accession.id = i.accession_id 
    LEFT JOIN
        enumeration_value ev 
            ON tc.type_id = ev.id  
    WHERE
        l.title LIKE @locationString   
    
	UNION
    ALL SELECT
        distinct ev.value,
        tc.indicator,
        tc.barcode,
        CONCAT('/repositories/',
        tc.repo_id,
        '/top_containers/',
        tc.id) as uri,
        '' AS 'title',
        '' as 'Resource Number',
        l.title,
        l.building,
        l.floor,
        l.room,
        l.area,
        l.coordinate_1_label,
        l.coordinate_1_indicator,
        l.coordinate_2_label,
        l.coordinate_2_indicator,
        l.coordinate_3_label,
        l.coordinate_3_indicator   
    FROM
        location l  
    LEFT JOIN
        top_container_housed_at_rlshp tcr 
            ON tcr.location_id = l.id 
    LEFT JOIN
        top_container tc 
            ON tc.id = tcr.top_container_id 
    LEFT JOIN
        top_container_link_rlshp tclr 
            ON tclr.top_container_id = tc.id 
    LEFT JOIN
        sub_container sc 
            ON tclr.sub_container_id = sc.id 
    LEFT JOIN
        enumeration_value ev 
            ON tc.type_id = ev.id   
    WHERE
        l.title LIKE @locationString  
        AND sc.instance_id IS null
	;
    