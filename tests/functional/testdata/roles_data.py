roles_creation_data = {
  "description": "Материалы для взрослых",
}

role_request_create = {
  "description": "Материалы для взрослых",
  "name": "+18"
}

invalid_too_long_name = {
  "description": "Материалы для взрослых",
  "name": "f" * 65
}

invalid_too_short_name = {
  "description": "Материалы для взрослых",
  "name": "f" * 0
}

del_query = f"""
    DELETE FROM public.roles
    WHERE NOT public.roles.name in ('Премиум', 'without role');
"""

del_query_role_perm = f"""
    DELETE FROM public.roles_permissions;
"""
