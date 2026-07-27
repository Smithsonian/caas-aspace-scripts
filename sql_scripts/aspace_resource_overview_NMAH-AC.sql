SET @repo_id = '20';

select r.id, r.repo_id, r.ead_id, r.title, r.finding_aid_filing_title, r.repository_processing_note, ev5.value as 'finding aid status', r.publish
, ev1.value as 'status'
, ev2.value as 'priority'
, e.number
, ev3.value as 'extent type'
, e.container_summary
, e.physical_details
, e.dimensions
, cm.processing_total_extent 
, ev4.value 'processing total extent type'

 from resource r 
 left join collection_management cm 
 on cm.resource_id = r.id

left join enumeration_value ev1
on cm.processing_status_id = ev1.id

left join enumeration_value ev2
on cm.processing_priority_id = ev2.id


left join extent e
on e.resource_id = r.id

left join enumeration_value ev3
on e.extent_type_id = ev3.id


left join enumeration_value ev4
on cm.processing_total_extent_type_id = ev4.id

left join enumeration_value ev5 
on r.finding_aid_status_id = ev5.id

where r.repo_id = @repo_id