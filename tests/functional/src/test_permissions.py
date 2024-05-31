import pytest
from http import HTTPStatus

from tests.functional.testdata.permissions_data import (
    permissions_creation_data,
    permission_request_create,
    invalid_too_long_name,
    invalid_too_short_name,
    del_query as del_query_permission
)
from tests.functional.testdata.roles_data import del_query as del_query_role, del_query_role_perm
from tests.functional.testdata.users_data import del_query as del_query_user, user_super_data, role_super_data
from tests.functional.testdata.tokens_data import UserClaims
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
async def test_list_permissions(
    make_get_request,
    postgres_write_data,
    postgres_execute,
    create_tokens,
    set_token,
    query_data,
    expected_answer,
):
    await postgres_execute(del_query_user)
    await postgres_execute(del_query_role_perm)
    await postgres_execute(del_query_role)
    await postgres_execute(del_query_permission)

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
        id.update(permissions_creation_data)
        id.update({"name": f"_{str(index)}"})
    if template:
        table = "permissions"
        await postgres_write_data(template, table)

    path = "/permissions/"
    response = await make_get_request(path, query_data, cookies=cookies)
    body, status, _ = response

    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        assert len(body) == expected_answer.get("length")


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            permission_request_create,
            {
                "status": HTTPStatus.OK,
                "description": "Не тот кто каждый поймет",
                "name": "Артхаус"
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
    ],
)
@pytest.mark.asyncio
async def test_create_permission(
    make_post_request,
    postgres_execute,
    postgres_write_data,
    create_tokens,
    set_token,
    query_data,
    expected_answer,
):
    await postgres_execute(del_query_user)
    await postgres_execute(del_query_role_perm)
    await postgres_execute(del_query_role)
    await postgres_execute(del_query_permission)

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

    path = "/permissions/"
    response = await make_post_request(path, body=query_data, cookies=cookies)
    body, status, _ = response

    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        assert body.get("description") == expected_answer.get("description")
        assert body.get("name") == expected_answer.get("name")


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {"permission_uuid": id_good_1},
            {
                "status": HTTPStatus.OK,
                "uuid": id_good_1,
                "keys": ["created_at", "updated_at", "uuid", "description", "name"],
            },
        ),
        ({"permission_uuid": id_bad}, {"status": HTTPStatus.NOT_FOUND}),
        ({"permission_uuid": id_invalid}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
    ],
)
@pytest.mark.asyncio
async def test_get_permission(
    make_get_request,
    postgres_write_data,
    postgres_execute,
    create_tokens,
    set_token,
    query_data,
    expected_answer,
):
    await postgres_execute(del_query_user)
    await postgres_execute(del_query_role_perm)
    await postgres_execute(del_query_role)
    await postgres_execute(del_query_permission)

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
    template[0].update(permissions_creation_data)
    template[0].update({"name": "Артхаус"})
    if template:
        table = "permissions"
        await postgres_write_data(template, table)

    path = f"/permissions/{query_data.get('permission_uuid')}"
    response = await make_get_request(path, cookies=cookies)
    body, status, _ = response

    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        assert body.get("uuid") == expected_answer.get("uuid")
        for key in body.keys():
            assert key in expected_answer.get("keys"), (
                "При GET-запросе к эндпоинту `auth/v1/permissions/{permission_uuid}` в ответе API должны "
                f"быть ключи `{expected_answer.get('keys')}`."
            )


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {"permission_uuid": id_good_1},
            {
                "status": HTTPStatus.OK,
                "uuid": id_good_1,
                "keys": ["created_at", "updated_at", "uuid", "description", "name"],
                "pathced_data": {
                    "description": "для самых тех"
                },
            },
        ),
        (
            {"permission_uuid": id_good_1},
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "pathced_data": {
                    "description": "",
                },
            }
        ),
    ],
)
@pytest.mark.asyncio
async def test_patch_permission(
    make_patch_request,
    postgres_write_data,
    postgres_execute,
    create_tokens,
    set_token,
    query_data,
    expected_answer,
):
    await postgres_execute(del_query_user)
    await postgres_execute(del_query_role_perm)
    await postgres_execute(del_query_role)
    await postgres_execute(del_query_permission)

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
    template[0].update(permissions_creation_data)
    template[0].update({"name": "+18"})
    if template:
        table = "permissions"
        await postgres_write_data(template, table)

    path = f"/permissions/{query_data.get('permission_uuid')}"
    response = await make_patch_request(path, body=expected_answer.get("pathced_data"), cookies=cookies)
    body, status, _ = response

    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        assert body.get("uuid") == expected_answer.get("uuid")
        for key in body.keys():
            assert key in expected_answer.get("keys"), (
                "При PATCH-запросе к эндпоинту `auth/v1/permissions/{permission_uuid}` в ответе API должны "
                f"быть ключи `{expected_answer.get('keys')}`."
            )


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {"permission_uuid": id_good_1},
            {
                "status": HTTPStatus.OK,
                "body": {
                    "code": HTTPStatus.OK,
                    "details": "Permission deleted successfully"
                },
            },
        ),
        ({"permission_uuid": id_bad}, {"status": HTTPStatus.NOT_FOUND}),
        ({"permission_uuid": id_invalid}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
    ],
)
@pytest.mark.asyncio
async def test_delete_permission(
    make_delete_request,
    postgres_write_data,
    postgres_execute,
    create_tokens,
    set_token,
    query_data,
    expected_answer,
):
    await postgres_execute(del_query_user)
    await postgres_execute(del_query_role_perm)
    await postgres_execute(del_query_role)
    await postgres_execute(del_query_permission)

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
    template[0].update(permissions_creation_data)
    template[0].update({"name": "Артхаус"})
    if template:
        table = "permissions"
        await postgres_write_data(template, table)

    path = f"/permissions/{query_data.get('permission_uuid')}"
    response = await make_delete_request(path, cookies=cookies)
    body, status, _ = response

    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        assert body == expected_answer.get("body")
