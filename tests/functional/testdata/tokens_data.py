from pydantic import BaseModel


class CacheTokens(BaseModel):
    access_token_cookie: str
    refresh_token_cookie: str


class UserClaims(BaseModel):
    user_uuid: str
    role_uuid: str

token_request_login = {
    "email": "very_admin@email.ru",
    "password": "[2/#&/%M9:aOIzJ-Xb.0Ncod?HoQih"
}

token_invalid_email_request_login = {
  "email": "example1mail.ru",
  "password": "[2/#&/%M9:aOIzJ-Xb.0Ncod?HoQih"
}

token_uregistered_email_request_login = {
  "email": "sdfsdfasfassadf@asddsag.ru",
  "password": "[2/#&/%M9:aOIzJ-Xb.0Ncod?HoQih"
}

token_invalid_password_request_login = {
  "email": "sdfsdfasfassadf@asddsag.ru",
  "password": "sadfsdf"
}

invalid_too_long_name = {
  "first_name": "f" * 65,
  "last_name": "Пупкин",
  "email": "example3@mail.ru",
  "password": "[2/#&/%M9:aOIzJ-Xb.0Ncod?HoQih"
}

invalid_too_short_name = {
  "first_name": "f" * 0,
  "last_name": "Пупкин",
  "email": "example4@mail.ru",
  "password": "[2/#&/%M9:aOIzJ-Xb.0Ncod?HoQih"
}

invalid_email = {
  "first_name": "Вася",
  "last_name": "Пупкин",
  "email": "examplemail.ru",
  "password": "[2/#&/%M9:aOIzJ-Xb.0Ncod?HoQih"
}
