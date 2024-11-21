SELECT 
  COUNT(*) 
FROM 
  (
    SELECT 
      do.id, 
      do.repo_id 
    FROM 
      digital_object AS do 
      JOIN lang_material ON lang_material.digital_object_id = do.id 
    UNION 
    SELECT 
      do.id, 
      do.repo_id 
    FROM 
      digital_object AS do 
      JOIN note ON note.digital_object_id = do.id 
    UNION 
    SELECT 
      do.id, 
      do.repo_id 
    FROM 
      digital_object AS do 
      JOIN extent ON extent.digital_object_id = do.id 
    UNION 
    SELECT 
      do.id, 
      do.repo_id 
    FROM 
      digital_object AS do 
      JOIN linked_agents_rlshp ON linked_agents_rlshp.digital_object_id = do.id 
    UNION 
    SELECT 
      do.id, 
      do.repo_id 
    FROM 
      digital_object AS do 
      JOIN subject_rlshp ON subject_rlshp.digital_object_id = do.id 
    UNION 
    SELECT 
      do.id, 
      do.repo_id 
    FROM 
      digital_object AS do 
      JOIN date ON date.digital_object_id = do.id 
    WHERE
      date.label_id != 2727
  ) AS T 
WHERE 
  T.repo_id NOT IN (11, 23, 50, 52)
