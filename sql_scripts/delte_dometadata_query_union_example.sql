SELECT 
  COUNT(*) 
FROM 
  (
    SELECT 
      do.id, 
      do.repo_id 
    FROM 
      digital_object AS do 
      RIGHT JOIN lang_material ON lang_material.digital_object_id = do.id 
    UNION 
    SELECT 
      do.id, 
      do.repo_id 
    FROM 
      digital_object AS do 
      RIGHT JOIN note ON note.digital_object_id = do.id 
    UNION 
    SELECT 
      do.id, 
      do.repo_id 
    FROM 
      digital_object AS do 
      RIGHT JOIN extent ON extent.digital_object_id = do.id 
    UNION 
    SELECT 
      do.id, 
      do.repo_id 
    FROM 
      digital_object AS do 
      RIGHT JOIN linked_agents_rlshp ON linked_agents_rlshp.digital_object_id = do.id 
    UNION 
    SELECT 
      do.id, 
      do.repo_id 
    FROM 
      digital_object AS do 
      RIGHT JOIN subject_rlshp ON subject_rlshp.digital_object_id = do.id 
    UNION 
    SELECT 
      do.id, 
      do.repo_id 
    FROM 
      digital_object AS do 
      RIGHT JOIN date ON date.digital_object_id = do.id 
    WHERE 
      date.label_id != 2727
  ) AS T 
WHERE 
  T.repo_id NOT IN (11, 23, 50, 52)
