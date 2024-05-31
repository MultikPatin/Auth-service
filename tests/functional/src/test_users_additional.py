import pytest
from http import HTTPStatus

from tests.functional.testdata.users_data import (
    users_creation_data,
    del_query as del_query_user,
    del_history_query,
    role_template,
    role_template_2,
    user_super_data,
    role_super_data,
    user_change_pass_data,
    user_invalid_pass_data
)
from tests.functional.testdata.roles_data import del_query as del_query_role, del_query_role_perm
from tests.functional.testdata.tokens_data import UserClaims
from tests.functional.testdata.base_data import (
    id_good_1,
    id_super,
    id_bad,
    id_invalid,
    id_role_premium,
)


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {"user_id": id_super, "data": user_change_pass_data},
            {
                "status": HTTPStatus.OK,
                "uuid": id_super,
                "new_password": "DJVkw6U&}b;q#V-D!7^;zl?52im2*B"
            },
        ),
        ({"user_id": id_super, "data": user_invalid_pass_data}, {"status": HTTPStatus.UNAUTHORIZED}),
    ],
)
@pytest.mark.asyncio
async def test_change_password(
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

    path = f"/users/{query_data.get('user_id')}/set_password/"
    response = await make_post_request(path, body=query_data.get("data"),cookies=cookies)
    body, status, _ = response
    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        path = f"/tokens/login/"
        body_ = {
            "email": user_super_data.get("email"),
            "password": expected_answer.get("new_password")
        }
        response = await make_post_request(path, body=body_,cookies=cookies)
        body, status, _ = response
        assert status == HTTPStatus.OK


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        # (
        #     {"user_uuid": id_super},
        #     {
        #         "status": HTTPStatus.OK,
        #         "uuid": id_super,
        #         "password": "[2/#&/%M9:aOIzJ-Xb.0Ncod?HoQih",
        #     },
        # ),
        (
            {"user_uuid": id_super},
            {
                "status": HTTPStatus.NOT_FOUND,
            },
        ),
        ({"user_uuid": id_good_1}, {"status": HTTPStatus.NOT_FOUND}),
    ],
)
@pytest.mark.asyncio
async def test_get_user_history(
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

    if expected_answer.get("status") == HTTPStatus.OK:
        path = f"/tokens/login/"
        body_ = {
            "email": user_super_data.get("email"),
            "password": expected_answer.get("password")
        }
        response = await make_post_request(path, body=body_,cookies=cookies)
        body, status, _ = response

    path = f"/users/{id_super}/history/"
    response = await make_get_request(path, query_data, cookies=cookies)
    body, status, _ = response
    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        assert body.get("user_uuid") == expected_answer.get("user_uuid")


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {"user_id": id_good_1},
            {
                "status": HTTPStatus.OK,
                "uuid": id_good_1,
                "keys": ["uuid", "first_name", "last_name", "email", "role"],
                "role_uuid": id_good_1
            },
        ),
        ({"user_id": id_bad}, {"status": HTTPStatus.NOT_FOUND}),
        ({"user_id": id_invalid}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
    ],
)
@pytest.mark.asyncio
async def test_get_user_role(
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

    path = f"/users/{query_data.get('user_id')}/role"
    response = await make_get_request(path, query_data, cookies)
    body, status, _ = response

    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        assert body.get("uuid") == expected_answer.get("uuid")
        for key in body.keys():
            assert key in expected_answer.get("keys"), (
                "При GET-запросе к эндпоинту `auth/v1/users/{user_id}/role` в ответе API должны "
                f"быть ключи `{expected_answer.get('keys')}`."
            )
        assert body.get("role").get("uuid") == expected_answer.get("role_uuid")


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {"user_id": id_good_1, "role_uuid": id_role_premium},
            {
                "status": HTTPStatus.OK,
                "uuid": id_good_1,
                "keys": ["uuid", "first_name", "last_name", "email", "role"],
            },
        ),
        (
            {"user_id": id_good_1, "role_uuid": id_invalid},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
            }
        ),
        (
            {"user_id": id_good_1, "role_uuid": id_bad},
            {
                "status": HTTPStatus.NOT_FOUND,
            }
        ),
    ],
)
@pytest.mark.asyncio
async def test_change_user_role(
    make_put_request,
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
        template_for_role = [role_template, role_template_2]
        template_for_role[0].update({"uuid": id_good_1})
        template_for_role[1].update({"uuid": id_role_premium})
        await postgres_write_data(template_for_role, table)
        table = "users"
        await postgres_write_data(template, table)

    path = f"/users/{query_data.get('user_id')}/roles/{query_data.get('role_uuid')}/"
    response = await make_put_request(path, query_data=query_data.get("role_uuid"), cookies=cookies)
    body, status, _ = response

    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        assert body.get("uuid") == expected_answer.get("uuid")
        for key in body.keys():
            assert key in expected_answer.get("keys"), (
                "При PUT-запросе к эндпоинту `auth/v1/users/{user_uuid}/role{role_uuid}` в ответе API должны "
                f"быть ключи `{expected_answer.get('keys')}`."
            )
        assert body.get("role").get("uuid") == query_data.get("role_uuid")
