select 
a.id
, a.repo_id
, a.title
, REPLACE(REPlACE(REPlACE(REPLACE(REPLACE(REPLACE(a.identifier, '[', ''), 'null', ''), ']', ''), '"', ''), ',,,', ''), ',,', '') as 'identifier'
, a.content_description
, a.condition_description
, a.disposition
, a.inventory
, a.provenance
, a.general_note
, ev2.value as 'acquisition_type'
, a.accession_date

, ud1.string_1 as 'museum_accession_id'
, ud1.date_1 as 'arrival_date'
, ev1.value as 'new_or_addition'

, ev3.value as 'status'
, ev4.value as 'priority'
-- , cm.processing_total_extent -- removed since processing total extent in collection management subrecord is not a field being used
-- , ev5.value 'processing total extent type' -- removed since extent type in collection management subrecord is not a field being used
, (select group_concat(ext.number, ' ', ev5.value separator ', ')
	from extent as ext
    join enumeration_value as ev5
		on ext.extent_type_id = ev5.id
    where a.id = ext.accession_id
    group by ext.accession_id) as 'extent'
, ext.container_summary as 'container summary'

 from accession a
 left join collection_management cm 
 on cm.accession_id = a.id

 left join user_defined ud1
 on ud1.accession_id = a.id 
 
 left join extent ext
 on ext.accession_id = a.id

left join enumeration_value ev1 
on ev1.id = ud1.enum_1_id

left join enumeration_value ev2 
on ev2.id = a.acquisition_type_id


left join enumeration_value ev3
on cm.processing_status_id = ev3.id

left join enumeration_value ev4
on cm.processing_priority_id = ev4.id

left join enumeration_value ev5
on ext.extent_type_id = ev5.id

where a.repo_id = '20'
;
