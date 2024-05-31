import pytest
from http import HTTPStatus


from tests.functional.testdata.users_data import (
    users_creation_data,
    user_request_create,
    invalid_too_long_name,
    invalid_too_short_name,
    invalid_email,
    role_template,
    del_query as del_query_user,
    del_history_query,
    user_super_data,
    role_super_data,
)
from tests.functional.testdata.tokens_data import UserClaims
from tests.functional.testdata.roles_data import del_query as del_query_role, del_query_role_perm
from tests.functional.testdata.base_data import (
    ids,
    id_super,
    id_good_1,
    id_bad,
    id_invalid
)

@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {},
            {"status": HTTPStatus.OK, "length": 10},
        ),
    ],
)
@pytest.mark.asyncio
async def test_list_users(
    make_get_request,
    postgres_write_data,
    postgres_execute,
    create_tokens,
    set_token,
    query_data,
    expected_answer,
):
    await postgres_execute(del_history_query)
    await postgres_execute(del_query_user)
    await postgres_execute(del_query_role_perm)
    await postgres_execute(del_query_role)

    await postgres_write_data([role_super_data], "roles")
    await postgres_write_data([user_super_data], "users")

    payload = UserClaims(user_uuid=id_super, role_uuid=id_super)
    tokens = await create_tokens(payload)
    if expected_answer.get("status") == HTTPStatus.OK:
        await set_token(query_data, tokens.refresh_token_cookie)

    cookies = {
        "access_token_cookie": tokens.access_token_cookie,
        "refresh_token_cookie": tokens.refresh_token_cookie
    }

    template = [{"uuid": id} for id in ids[:expected_answer.get("length")]]
    for index, id in enumerate(template):
        id.update(users_creation_data)
        id.update({"email": f"example{str(index)}@mail.ru", "role_uuid": id_good_1})
    if template:
        table = "roles"
        template_for_role = [role_template]
        template_for_role[0].update({"uuid": id_good_1})
        await postgres_write_data(template_for_role, table)
        table = "users"
        await postgres_write_data(template, table)

    path = "/users/"
    response = await make_get_request(path, cookies=cookies)
    body, status, _ = response
    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        assert len(body)-1 == expected_answer.get("length")


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {"user_id": id_good_1},
            {
                "status": HTTPStatus.OK,
                "body": {
                    "code": HTTPStatus.OK,
                    "details": "User deleted successfully"
                },
            },
        ),
        ({"user_id": id_bad}, {"status": HTTPStatus.NOT_FOUND}),
        ({"user_id": id_invalid}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
    ],
)
@pytest.mark.asyncio
async def test_delete_user(
    make_delete_request,
    postgres_write_data,
    postgres_execute,
    create_tokens,
    set_token,
    query_data,
    expected_answer,
):
    await postgres_execute(del_history_query)
    await postgres_execute(del_query_user)
    await postgres_execute(del_query_role_perm)
    await postgres_execute(del_query_role)

    await postgres_write_data([role_super_data], "roles")
    await postgres_write_data([user_super_data], "users")

    payload = UserClaims(user_uuid=id_super, role_uuid=id_super)
    tokens = await create_tokens(payload)
    if expected_answer.get("status") == HTTPStatus.OK:
        await set_token(query_data, tokens.refresh_token_cookie)

    cookies = {
        "access_token_cookie": tokens.access_token_cookie,
        "refresh_token_cookie": tokens.refresh_token_cookie
    }

    template = [{"uuid": id_good_1}]
    template[0].update(users_creation_data)
    template[0].update({"email": "example@mail.ru", "role_uuid": id_good_1})
    if template:
        table = "roles"
        template_for_role = [role_template]
        template_for_role[0].update({"uuid": id_good_1})
        await postgres_write_data(template_for_role, table)
        table = "users"
        await postgres_write_data(template, table)


    path = f"/users/{query_data.get('user_id')}"
    response = await make_delete_request(path, cookies=cookies)
    body, status, _ = response

    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        assert body == expected_answer.get("body")


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            user_request_create,
            {
                "status": HTTPStatus.OK,
                "first_name": "Вася",
                "last_name": "Пупкин",
                "email": "exemple1@mail.ru",
                "is_superuser": False
            },
        ),
        (
            invalid_too_long_name,
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY},
        ),
        (
            invalid_too_short_name,
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY},
        ),
        (
            invalid_email,
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY},
        ),
    ],
)
@pytest.mark.asyncio
async def test_create_user(
    make_post_request,
    postgres_execute,
    postgres_write_data,
    create_tokens,
    set_token,
    query_data,
    expected_answer,
):
    await postgres_execute(del_history_query)
    await postgres_execute(del_query_user)
    await postgres_execute(del_query_role_perm)
    await postgres_execute(del_query_role)

    await postgres_write_data([role_super_data], "roles")
    await postgres_write_data([user_super_data], "users")

    payload = UserClaims(user_uuid=id_super, role_uuid=id_super)
    tokens = await create_tokens(payload)
    if expected_answer.get("status") == HTTPStatus.OK:
        await set_token(query_data, tokens.refresh_token_cookie)

    cookies = {
        "access_token_cookie": tokens.access_token_cookie,
        "refresh_token_cookie": tokens.refresh_token_cookie
    }

    path = "/users/"
    response = await make_post_request(path, body=query_data, cookies=cookies)
    body, status, _ = response

    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        assert body.get("first_name") == expected_answer.get("first_name")
        assert body.get("last_name") == expected_answer.get("last_name")
        assert body.get("email") == expected_answer.get("email")
        assert body.get("is_superuser") == expected_answer.get("is_superuser")




@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {"user_id": id_good_1},
            {
                "status": HTTPStatus.OK,
                "uuid": id_good_1,
                "keys": ["created_at", "updated_at", "uuid", "first_name", "last_name", "email", "is_superuser", "role_uuid"],
            },
        ),
        ({"user_id": id_bad}, {"status": HTTPStatus.NOT_FOUND}),
        ({"user_id": id_invalid}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
    ],
)
@pytest.mark.asyncio
async def test_get_user(
    make_get_request,
    postgres_write_data,
    postgres_execute,
    create_tokens,
    set_token,
    query_data,
    expected_answer,
):
    await postgres_execute(del_history_query)
    await postgres_execute(del_query_user)
    await postgres_execute(del_query_role_perm)
    await postgres_execute(del_query_role)

    await postgres_write_data([role_super_data], "roles")
    await postgres_write_data([user_super_data], "users")

    payload = UserClaims(user_uuid=id_super, role_uuid=id_super)
    tokens = await create_tokens(payload)
    if expected_answer.get("status") == HTTPStatus.OK:
        await set_token(query_data, tokens.refresh_token_cookie)

    cookies = {
        "access_token_cookie": tokens.access_token_cookie,
        "refresh_token_cookie": tokens.refresh_token_cookie
    }

    template = [{"uuid": id_good_1}]
    template[0].update(users_creation_data)
    template[0].update({"email": "example@mail.ru", "role_uuid": id_good_1})
    if template:
        table = "roles"
        template_for_role = [role_template]
        template_for_role[0].update({"uuid": id_good_1})
        await postgres_write_data(template_for_role, table)
        table = "users"
        await postgres_write_data(template, table)

    path = f"/users/{query_data.get('user_id')}"
    response = await make_get_request(path, cookies=cookies)
    body, status, _ = response

    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        assert body.get("uuid") == expected_answer.get("uuid")
        for key in body.keys():
            assert key in expected_answer.get("keys"), (
                "При GET-запросе к эндпоинту `auth/v1/users/{user_id}` в ответе API должны "
                f"быть ключи `{expected_answer.get('keys')}`."
            )


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {"user_id": id_good_1},
            {
                "status": HTTPStatus.OK,
                "uuid": id_good_1,
                "keys": ["created_at", "updated_at", "uuid", "first_name", "last_name", "email", "is_superuser", "role_uuid"],
                "pathced_data": {
                    "first_name": "Эдик",
                    "last_name": "Эриксон",
                },
            },
        ),
        (
            {"user_id": id_good_1},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "pathced_data": {
                    "first_name": "Эдик",
                },
            }
        ),
        (
            {"user_id": id_good_1},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "pathced_data": {
                    "last_name": "Эриксон",
                },
            }
        ),
    ],
)
@pytest.mark.asyncio
async def test_patch_user(
    make_patch_request,
    postgres_write_data,
    postgres_execute,
    create_tokens,
    set_token,
    query_data,
    expected_answer,
):
    await postgres_execute(del_history_query)
    await postgres_execute(del_query_user)
    await postgres_execute(del_query_role_perm)
    await postgres_execute(del_query_role)

    await postgres_write_data([role_super_data], "roles")
    await postgres_write_data([user_super_data], "users")

    payload = UserClaims(user_uuid=id_super, role_uuid=id_super)
    tokens = await create_tokens(payload)
    if expected_answer.get("status") == HTTPStatus.OK:
        await set_token(query_data, tokens.refresh_token_cookie)

    cookies = {
        "access_token_cookie": tokens.access_token_cookie,
        "refresh_token_cookie": tokens.refresh_token_cookie
    }

    template = [{"uuid": id_good_1}]

    template[0].update(users_creation_data)
    template[0].update({"email": "example@mail.ru", "role_uuid": id_good_1})

    if template:
        table = "roles"
        template_for_role = [role_template]
        template_for_role[0].update({"uuid": id_good_1})
        await postgres_write_data(template_for_role, table)
        table = "users"
        await postgres_write_data(template, table)

    path = f"/users/{query_data.get('user_id')}"
    response = await make_patch_request(path, body=expected_answer.get("pathced_data"), cookies=cookies)
    body, status, _ = response

    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        assert body.get("uuid") == expected_answer.get("uuid")
        for key in body.keys():
            assert key in expected_answer.get("keys"), (
                "При PATCH-запросе к эндпоинту `auth/v1/users/{user_id}` в ответе API должны "
                f"быть ключи `{expected_answer.get('keys')}`."
            )


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {"user_uuid": id_super},
            {
                "status": HTTPStatus.OK,
                "uuid": id_super,
                "password": "[2/#&/%M9:aOIzJ-Xb.0Ncod?HoQih",
            }
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_me(
    make_get_request,
    make_post_request,
    postgres_write_data,
    postgres_execute,
    create_tokens,
    set_token,
    query_data,
    expected_answer,
):
    await postgres_execute(del_history_query)
    await postgres_execute(del_query_user)
    await postgres_execute(del_query_role_perm)
    await postgres_execute(del_query_role)

    await postgres_write_data([role_super_data], "roles")
    await postgres_write_data([user_super_data], "users")

    payload = UserClaims(user_uuid=id_super, role_uuid=id_super)
    tokens = await create_tokens(payload)
    if expected_answer.get("status") == HTTPStatus.OK:
        await set_token(query_data, tokens.refresh_token_cookie)

    cookies = {
        "access_token_cookie": tokens.access_token_cookie,
        "refresh_token_cookie": tokens.refresh_token_cookie
    }

    if expected_answer.get("statis") == HTTPStatus.OK:
        path = f"/tokens/login/"
        body_ = {
            "email": user_super_data.get("email"),
            "password": expected_answer.get("password")
        }
        response = await make_post_request(path, body=body_,cookies=cookies)
        body, status, _ = response

    path = f"/users/me/"
    response = await make_get_request(path, cookies=cookies)
    body, status, _ = response

    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        assert body.get("uuid") == expected_answer.get("uuid")
