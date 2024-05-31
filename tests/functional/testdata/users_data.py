from werkzeug.security import generate_password_hash
from tests.functional.testdata.base_data import (
    id_super,
)


user_super_data = {
    "uuid": id_super,
    "first_name": "admin",
    "last_name": "very_big_admin",
    "email": "very_admin@email.ru",
    "password": generate_password_hash("[2/#&/%M9:aOIzJ-Xb.0Ncod?HoQih"),
    "is_superuser": True,
    "role_uuid": id_super,
}

role_super_data = {
    "name": "Роль админ",
    "uuid": id_super,
    "description": "Админская роль",
}

user_change_pass_data = {
    "new_password": generate_password_hash("DJVkw6U&}b;q#V-D!7^;zl?52im2*B"),
    "current_password": "[2/#&/%M9:aOIzJ-Xb.0Ncod?HoQih"
}

user_invalid_pass_data = {
    "new_password": generate_password_hash("DJVkw6U&}b;q#V-D!7^;zl?52im2*B"),
    "current_password": "sdafsadfd"
}

users_creation_data = {
    "first_name": "Вася",
    "last_name": "Пупкин",
    "password": generate_password_hash("[2/#&/%M9:aOIzJ-Xb.0Ncod?HoQih"),
    "is_superuser": False,
}

user_request_create = {
    "first_name": "Вася",
    "last_name": "Пупкин",
    "email": "exemple1@mail.ru",
    "password": "[2/#&/%M9:aOIzJ-Xb.0Ncod?HoQih"
}

invalid_too_long_name = {
    "first_name": "f" * 65,
    "last_name": "Пупкин",
    "email": "exemple3@mail.ru",
    "password": "[2/#&/%M9:aOIzJ-Xb.0Ncod?HoQih"
}

invalid_too_short_name = {
    "first_name": "f" * 0,
    "last_name": "Пупкин",
    "email": "exemple4@mail.ru",
    "password": "[2/#&/%M9:aOIzJ-Xb.0Ncod?HoQih"
}

invalid_email = {
    "first_name": "Вася",
    "last_name": "Пупкин",
    "email": "exemplemail.ru",
    "password": "[2/#&/%M9:aOIzJ-Xb.0Ncod?HoQih"
}

role_template = {
    "name": "Test role 1",
    "description": "test role secription",
}

role_template_2 = {
    "name": "Test role 2",
    "description": "test role secription",
}

history_data = {
    "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "user_uuid": "id_super",
    "ip_address": "127.0.0.1:8000",
    "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

del_query = f"""
    DELETE FROM public.users
    WHERE NOT public.users.email = 'my_test@mail.ru';
"""

del_history_query = f"""
    DELETE FROM public.login_history
"""
