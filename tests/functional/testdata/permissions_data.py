from tests.functional.testdata.base_data import (
    id_good_1,
    id_good_2
)


permissions_creation_data = {
    "description": "Не тот кто каждый поймет",
}

permission_1 = {
    "uuid": id_good_1,
    "description": "Не тот кто каждый поймет",
    "name": "Артхаус"
}

permission_2 = {
    "uuid": id_good_2,
    "description": "кмоу-то интересно",
    "name": "Спорт"
}
permission_request_create = {
    "description": "Не тот кто каждый поймет",
    "name": "Артхаус"
}

invalid_too_long_name = {
    "description": "Не тот кто каждый поймет",
    "name": "f" * 65
}

invalid_too_short_name = {
    "description": "Не тот кто каждый поймет",
    "name": "f" * 0
}

del_query = f"""
    DELETE FROM public.permissions;
"""
