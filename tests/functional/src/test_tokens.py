import pytest
from http import HTTPStatus

from tests.functional.testdata.tokens_data import (
    token_request_login,
    token_invalid_email_request_login,
    token_uregistered_email_request_login,
    token_invalid_password_request_login,
)
from tests.functional.testdata.tokens_data import UserClaims
from tests.functional.testdata.roles_data import del_query as del_query_role, del_query_role_perm
from tests.functional.testdata.users_data import del_query as del_query_user, del_history_query, user_super_data, role_super_data
from tests.functional.testdata.base_data import (
    id_super,
    id_good_1,
    id_good_2,
    invalid_secret_key,
)


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            token_request_login,
            {
                "status": HTTPStatus.OK,
            },
        ),
        (
            token_uregistered_email_request_login,
            {"status": HTTPStatus.UNAUTHORIZED},
        ),
        (
            token_invalid_password_request_login,
            {"status": HTTPStatus.UNAUTHORIZED},
        ),
        (
            token_invalid_email_request_login,
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY},
        ),
    ],
)
@pytest.mark.asyncio
async def test_login(
    make_post_request,
    postgres_write_data,
    postgres_execute,
    validate_token,
    get_tokens,
    clear_cache,
    query_data,
    expected_answer,
):
    await postgres_execute(del_history_query)
    await postgres_execute(del_query_user)
    await postgres_execute(del_query_role_perm)
    await postgres_execute(del_query_role)
    await clear_cache()

    await postgres_write_data([role_super_data], "roles")
    await postgres_write_data([user_super_data], "users")

    path = "/tokens/login/"
    response = await make_post_request(path, body=query_data)
    _, status, cookies = response

    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        access_token_cookie = cookies.get('access_token_cookie').coded_value
        refresh_token_cookie = cookies.get('refresh_token_cookie').coded_value
        user_data = await validate_token(access_token_cookie)
        assert user_data.get("user_uuid") == id_super
        cahche_token = [str(token, encoding=("utf-8")) for token in await get_tokens(id_super)]
        assert refresh_token_cookie in cahche_token


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            id_good_1,
            {"status": HTTPStatus.OK},
        ),
        (
            id_good_2,
            {"status": HTTPStatus.UNAUTHORIZED},
        ),
    ],
)
@pytest.mark.asyncio
async def test_refresh(
    make_post_request,
    validate_token,
    create_tokens,
    set_token,
    get_tokens,
    clear_cache,
    query_data,
    expected_answer,
):
    await clear_cache()

    payload = UserClaims(user_uuid=query_data, role_uuid=query_data)
    tokens = await create_tokens(payload)
    if expected_answer.get("status") == HTTPStatus.OK:
        await set_token(query_data, tokens.refresh_token_cookie)
    path = "/tokens/refresh/"
    cookies = {
        "access_token_cookie": tokens.access_token_cookie,
        "refresh_token_cookie": tokens.refresh_token_cookie
    }
    response = await make_post_request(path, cookies=cookies)
    _, status, cookies = response

    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        access_token_cookie = cookies.get('access_token_cookie').coded_value
        user_data = await validate_token(access_token_cookie)
        assert user_data.get("user_uuid") == query_data
        cahche_tokens = [str(token, encoding=("utf-8")) for token in await get_tokens(query_data)]
        assert not tokens.refresh_token_cookie  in cahche_tokens
        assert cookies.get('refresh_token_cookie').coded_value in cahche_tokens


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {},
            {"status": HTTPStatus.OK},
        ),
        (
            invalid_secret_key,
            {"status": HTTPStatus.UNAUTHORIZED},
        ),
    ],
)
@pytest.mark.asyncio
async def test_verify(
    make_post_request,
    create_tokens,
    clear_cache,
    query_data,
    expected_answer,
):
    await clear_cache()

    payload = UserClaims(user_uuid=id_good_1, role_uuid=id_good_1)
    if query_data:
        tokens = await create_tokens(payload, secret_key=query_data)
    else:
        tokens = await create_tokens(payload)
    path = "/tokens/verify/"
    cookies = {
        "access_token_cookie": tokens.access_token_cookie,
        "refresh_token_cookie": tokens.refresh_token_cookie
    }
    response = await make_post_request(path, cookies=cookies)
    _, status, _ = response

    assert status == expected_answer.get("status")


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {"for_all_sessions": 0},
            {"status": HTTPStatus.OK},
        ),
        (
            {"for_all_sessions": 1},
            {"status": HTTPStatus.OK},
        ),
    ],
)
@pytest.mark.asyncio
async def test_logout(
    make_post_request,
    create_tokens,
    set_token,
    get_tokens,
    clear_cache,
    query_data,
    expected_answer,
):
    await clear_cache()

    payload = UserClaims(user_uuid=id_good_1, role_uuid=id_good_1)
    tokens = await create_tokens(payload)
    await set_token(id_good_1, tokens.refresh_token_cookie)

    path = "/tokens/logout/"
    cookies = {
        "access_token_cookie": tokens.access_token_cookie,
        "refresh_token_cookie": tokens.refresh_token_cookie
    }
    response = await make_post_request(path, query_data=query_data, cookies=cookies)
    _, status, _ = response

    assert status == expected_answer.get("status")
    if status == HTTPStatus.OK:
        cache_tokens = await get_tokens(query_data)
        if cache_tokens and not query_data.get("for_all_sessions"):
            cahche_tokens = [str(token, encoding=("utf-8")) for token in cache_tokens]
            assert not tokens.refresh_token_cookie in cahche_tokens
