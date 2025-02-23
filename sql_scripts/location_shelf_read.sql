SET @locationString = 'NMAH, Basement, CB-023%';

    SELECT DISTINCT
        REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(resource.identifier,
            ',', '.'),
            '"', ''),
            ']', ''),
            '[', ''),
            '.null', '') AS 'Resource Number',
        resource.title AS 'Resource Title',
        l.title AS 'Location Title',
        SUBSTRING(l.title,
            LOCATE('[', l.title) + 1,
            LOCATE(']', l.title) -LOCATE('[', l.title) - 1) AS 'Coordinate String',
	    ev.value AS 'Container Type',
        tc.indicator AS 'Container Indicator',
        cp.name AS 'Container Profile',
        tc.barcode,
        CONCAT('/repositories/',
            tc.repo_id,
            '/top_containers/',
            tc.id) AS uri,
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
            ON i.id = sc.instance_id  
    JOIN
        archival_object ao 
            ON ao.id = i.archival_object_id 
    JOIN
        resource 
            ON ao.root_record_id = resource.id 
    LEFT JOIN
        enumeration_value ev 
            ON tc.type_id = ev.id  
    LEFT JOIN
    	top_container_profile_rlshp tcpr
    		ON tcpr.top_container_id = tc.id
    LEFT JOIN container_profile cp
    		ON tcpr.container_profile_id = cp.id
	WHERE
        l.title LIKE @locationString

    UNION ALL
    SELECT DISTINCT
        REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(resource.identifier,
            ',', '.'),
            '"', ''),
            ']', ''),
            '[', ''),
            '.null', '') AS 'Resource Number',
        resource.title AS 'Resource Title',
        l.title AS 'Location Title',
        SUBSTRING(l.title,
            LOCATE('[', l.title) + 1,
            LOCATE(']', l.title) -LOCATE('[', l.title) - 1) AS 'Coordinate String',
		ev.value AS 'Container Type',
        tc.indicator AS 'Container Indicator',
        cp.name AS 'Container Profile',
        tc.barcode,
        CONCAT('/repositories/',
            tc.repo_id,
            '/top_containers/',
            tc.id) AS uri,
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
            ON i.id = sc.instance_id 
    JOIN
        resource 
            ON resource.id = i.resource_id 
    LEFT JOIN
        enumeration_value ev 
            ON tc.type_id = ev.id   
    LEFT JOIN
    	top_container_profile_rlshp tcpr
    		ON tcpr.top_container_id = tc.id
    LEFT JOIN 
        container_profile cp
    		ON tcpr.container_profile_id = cp.id		
    WHERE
        l.title LIKE @locationString

    UNION ALL
    SELECT DISTINCT
        REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(resource.identifier,
            ',', '.'),
            '"', ''),
            ']', ''),
            '[', ''),
            '.null', '') AS 'Resource Number',
        accession.title AS 'Resource Title',
        l.title AS 'Location Title',
        SUBSTRING(l.title,
             LOCATE('[', l.title) + 1,
             LOCATE(']', l.title) -LOCATE('[', l.title) - 1) AS 'Coordinate String',
		ev.value AS 'Container Type',
        tc.indicator AS 'Container Indicator',
        cp.name AS 'Container Profile',
        tc.barcode,
        CONCAT('/repositories/',
            tc.repo_id,
            '/top_containers/',
            tc.id) AS uri,
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
            ON i.id = sc.instance_id 
    JOIN
        accession 
            ON accession.id = i.accession_id 
    LEFT JOIN
        enumeration_value ev 
            ON tc.type_id = ev.id  
    LEFT JOIN
    	top_container_profile_rlshp tcpr
    		ON tcpr.top_container_id = tc.id
    LEFT JOIN 
        container_profile cp
    		ON tcpr.container_profile_id = cp.id
    WHERE
        l.title LIKE @locationString
        
    UNION ALL
    SELECT DISTINCT
        '' as 'Resource Number',
        '' AS 'Resource Title',
        l.title AS 'Location Title',
        SUBSTRING(l.title,
             LOCATE('[', l.title) + 1,
             LOCATE(']', l.title) -LOCATE('[', l.title) - 1) AS 'Coordinate String',
		ev.value AS 'Container Type',
        tc.indicator AS 'Container Indicator',
        cp.name AS 'Container Profile',
        tc.barcode,
        CONCAT('/repositories/',
            tc.repo_id,
            '/top_containers/',
            tc.id) AS uri,
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
    LEFT JOIN
    	top_container_profile_rlshp tcpr
    		ON tcpr.top_container_id = tc.id
    LEFT JOIN 
        container_profile cp
    	    ON tcpr.container_profile_id = cp.id

    WHERE
        l.title LIKE @locationString 
            AND sc.instance_id IS null
    ;
