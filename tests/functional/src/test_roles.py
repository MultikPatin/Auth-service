import pytest
from http import HTTPStatus

from tests.functional.testdata.roles_data import (
    roles_creation_data,
    role_request_create,
    invalid_too_long_name,
    invalid_too_short_name,
    del_query as del_query_role,
    del_query_role_perm
)
from tests.functional.testdata.tokens_data import UserClaims
from tests.functional.testdata.users_data import del_query as del_query_user, user_super_data, role_super_data
from tests.functional.testdata.permissions_data import del_query as del_query_permissions, permission_1, permission_2
from tests.functional.testdata.base_data import (
    ids,
    id_super,
    id_good_1,
    id_good_2,
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
async def test_list_roles(
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
    await postgres_execute(del_query_permissions)

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
        id.update(roles_creation_data)
        id.update({"name": f"+18{str(index)}"})
    if template:
        table = "roles"
        await postgres_write_data(template, table)

    path = "/roles/"
    response = await make_get_request(path, query_data, cookies=cookies)
    body, status, _ = response

    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        # -2 - for base roles
        assert len(body) - 2 == expected_answer.get("length")


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            role_request_create,
            {
                "status": HTTPStatus.OK,
                "description": "Материалы для взрослых",
                "name": "+18"
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
async def test_create_role(
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
    await postgres_execute(del_query_permissions)

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

    path = "/roles/"
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
            {"role_uuid": id_good_1},
            {
                "status": HTTPStatus.OK,
                "uuid": id_good_1,
                "keys": ["created_at", "updated_at", "uuid", "description", "name"],
            },
        ),
        ({"role_uuid": id_bad}, {"status": HTTPStatus.NOT_FOUND}),
        ({"role_uuid": id_invalid}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
    ],
)
@pytest.mark.asyncio
async def test_get_role(
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
    await postgres_execute(del_query_permissions)

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

    template[0].update(roles_creation_data)
    template[0].update({"name": "+18"})

    if template:
        table = "roles"
        await postgres_write_data(template, table)

    path = f"/roles/{query_data.get('role_uuid')}"
    response = await make_get_request(path, cookies=cookies)
    body, status, _ = response

    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        assert body.get("uuid") == expected_answer.get("uuid")
        for key in body.keys():
            assert key in expected_answer.get("keys"), (
                "При GET-запросе к эндпоинту `auth/v1/roles/{role_uuid}` в ответе API должны "
                f"быть ключи `{expected_answer.get('keys')}`."
            )


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {"role_uuid": id_good_1},
            {
                "status": HTTPStatus.OK,
                "uuid": id_good_1,
                "keys": ["created_at", "updated_at", "uuid", "description", "name"],
                "pathced_data": {
                    "description": "Приостановленный доступ"
                },
            },
        ),
        (
            {"role_uuid": id_good_1},
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
async def test_patch_role(
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
    await postgres_execute(del_query_permissions)

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

    template[0].update(roles_creation_data)
    template[0].update({"name": "+18"})

    if template:
        table = "roles"
        await postgres_write_data(template, table)

    path = f"/roles/{query_data.get('role_uuid')}"
    response = await make_patch_request(path, body=expected_answer.get("pathced_data"), cookies=cookies)
    body, status, _ = response

    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        assert body.get("uuid") == expected_answer.get("uuid")
        for key in body.keys():
            assert key in expected_answer.get("keys"), (
                "При PATCH-запросе к эндпоинту `auth/v1/roles/{role_uuid}` в ответе API должны "
                f"быть ключи `{expected_answer.get('keys')}`."
            )


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {"role_uuid": id_good_1},
            {
                "status": HTTPStatus.OK,
                "body": {
                    "code": HTTPStatus.OK,
                    "details": "Role deleted successfully"
                },
            },
        ),
        ({"role_uuid": id_bad}, {"status": HTTPStatus.NOT_FOUND}),
        ({"role_uuid": id_invalid}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
    ],
)
@pytest.mark.asyncio
async def test_delete_role(
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
    await postgres_execute(del_query_permissions)

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

    template[0].update(roles_creation_data)
    template[0].update({"name": "+18"})

    if template:
        table = "roles"
        await postgres_write_data(template, table)

    path = f"/roles/{query_data.get('role_uuid')}"
    response = await make_delete_request(path, cookies=cookies)
    body, status, _ = response

    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        assert body == expected_answer.get("body")


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {"role_uuid": id_super},
            {
                "status": HTTPStatus.OK,
                "uuid": id_super,
            },
        ),
        ({"role_uuid": id_bad}, {"status": HTTPStatus.NOT_FOUND}),
        ({"role_uuid": id_invalid}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
    ],
)
@pytest.mark.asyncio
async def test_get_role_permissions(
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
    await postgres_execute(del_query_permissions)

    await postgres_write_data([role_super_data], "roles")
    await postgres_write_data([user_super_data], "users")

    await postgres_write_data([permission_1], "permissions")
    await postgres_write_data([permission_2], "permissions")
    relations = [
        {
            "uuid": id_good_1,
            "role_uuid": id_super,
            "permission_uuid": id_good_1
        },
        {
            "uuid": id_good_2,
            "role_uuid": id_super,
            "permission_uuid": id_good_2
        }
    ]
    await postgres_write_data(relations, "roles_permissions")

    payload = UserClaims(user_uuid=id_super, role_uuid=id_super)
    tokens = await create_tokens(payload)
    if expected_answer.get("status") == HTTPStatus.OK:
        await set_token(query_data, tokens.refresh_token_cookie)

    cookies = {
        "access_token_cookie": tokens.access_token_cookie,
        "refresh_token_cookie": tokens.refresh_token_cookie
    }

    path = f"/roles/{query_data.get('role_uuid')}/permissions/"
    response = await make_get_request(path, query_data=query_data, cookies=cookies)
    body, status, _ = response
    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        assert body.get("uuid") == expected_answer.get("uuid")


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {"role_uuid": id_super, "permission_uuid": id_good_1},
            {
                "status": HTTPStatus.OK,
                "uuid": id_super,
                "permissions": [{"uuid": id_good_1, "name": "Артхаус"}]
            },
        ),
        ({"role_uuid": id_bad, "permission_uuid": id_good_1}, {"status": HTTPStatus.NOT_FOUND}),
        ({"role_uuid": id_invalid, "permission_uuid": id_good_1}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
    ],
)
@pytest.mark.asyncio
async def test_add_role_permissions(
    make_post_request,
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
    await postgres_execute(del_query_permissions)

    await postgres_write_data([role_super_data], "roles")
    await postgres_write_data([user_super_data], "users")

    await postgres_write_data([permission_1], "permissions")
    await postgres_write_data([permission_2], "permissions")

    payload = UserClaims(user_uuid=id_super, role_uuid=id_super)
    tokens = await create_tokens(payload)
    if expected_answer.get("status") == HTTPStatus.OK:
        await set_token(query_data, tokens.refresh_token_cookie)

    cookies = {
        "access_token_cookie": tokens.access_token_cookie,
        "refresh_token_cookie": tokens.refresh_token_cookie
    }

    path = f"/roles/{query_data.get('role_uuid')}/permissions/{query_data.get('permission_uuid')}/"
    response = await make_post_request(path, query_data=query_data, cookies=cookies)
    body, status, _ = response
    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        assert body.get("uuid") == expected_answer.get("uuid")
        assert body.get("permissions") == expected_answer.get("permissions")


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {"role_uuid": id_super, "permission_uuid": id_good_1},
            {
                "status": HTTPStatus.OK,
            },
        ),
        ({"role_uuid": id_bad, "permission_uuid": id_good_1}, {"status": HTTPStatus.NOT_FOUND}),
        ({"role_uuid": id_invalid, "permission_uuid": id_good_1}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
    ],
)
@pytest.mark.asyncio
async def test_remove_role_permissions(
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
    await postgres_execute(del_query_permissions)

    await postgres_write_data([role_super_data], "roles")
    await postgres_write_data([user_super_data], "users")

    await postgres_write_data([permission_1], "permissions")
    await postgres_write_data([permission_2], "permissions")

    await postgres_write_data([permission_1], "permissions")
    await postgres_write_data([permission_2], "permissions")
    relations = [
        {
            "uuid": id_good_1,
            "role_uuid": id_super,
            "permission_uuid": id_good_1
        },
        {
            "uuid": id_good_2,
            "role_uuid": id_super,
            "permission_uuid": id_good_2
        }
    ]
    await postgres_write_data(relations, "roles_permissions")

    payload = UserClaims(user_uuid=id_super, role_uuid=id_super)
    tokens = await create_tokens(payload)
    if expected_answer.get("status") == HTTPStatus.OK:
        await set_token(query_data, tokens.refresh_token_cookie)

    cookies = {
        "access_token_cookie": tokens.access_token_cookie,
        "refresh_token_cookie": tokens.refresh_token_cookie
    }

    path = f"/roles/{query_data.get('role_uuid')}/permissions/{query_data.get('permission_uuid')}/"
    response = await make_delete_request(path, query_data=query_data, cookies=cookies)
    _, status, _ = response
    assert status == expected_answer.get("status")
