select repo.repo_code, u.username, u.name, g.description
  from group_user gu, `group` g, user u, repository repo
  where gu.group_id = g.id
  and gu.user_id = u.id
  and g.repo_id = repo.id
  and is_active_user = 1  -- can set this to 0 to check for inactive users still attached to user groups within repos
  and gu.user_id in (
    select user_id
    from group_user
    group by user_id
--     having count(*) > 1 -- can leave this out - checks for more than 1 user group per person
  )
  order by username, description