from httpx import AsyncClient

from tests.helpers import auth_header, signup_and_login


async def _create_bill(client: AsyncClient, token: str, name: str = "Internet bill"):
    return await client.post(
        "/bills/",
        json={
            "name": name,
            "storage_key": "s3://bucket/internet.pdf",
            "file_hash": "hash-internet-1",
        },
        headers=auth_header(token),
    )


async def _create_flag(
    client: AsyncClient,
    token: str,
    bill_id: str,
    flag_type: str = "duplicate",
    reason: str = "Looks like a duplicate charge",
):
    return await client.post(
        f"/bills/{bill_id}/flags/",
        json={"flag_type": flag_type, "reason": reason},
        headers=auth_header(token),
    )


async def test_flag_crud_happy_path(client: AsyncClient) -> None:
    token = await signup_and_login(client, "flag-owner@example.com", "flag_owner")
    bill_id = (await _create_bill(client, token)).json()["id"]

    create_resp = await _create_flag(client, token, bill_id)
    assert create_resp.status_code == 201
    flag = create_resp.json()
    flag_id = flag["id"]
    assert flag["flag_type"] == "duplicate"
    assert flag["status"] == "open"

    get_resp = await client.get(f"/bills/{bill_id}/flags/{flag_id}", headers=auth_header(token))
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == flag_id

    list_resp = await client.get(f"/bills/{bill_id}/flags/", headers=auth_header(token))
    assert list_resp.status_code == 200
    assert any(f["id"] == flag_id for f in list_resp.json())

    update_resp = await client.patch(
        f"/bills/{bill_id}/flags/{flag_id}",
        json={"status": "resolved"},
        headers=auth_header(token),
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "resolved"

    delete_resp = await client.delete(
        f"/bills/{bill_id}/flags/{flag_id}", headers=auth_header(token)
    )
    assert delete_resp.status_code == 204

    missing_resp = await client.get(f"/bills/{bill_id}/flags/{flag_id}", headers=auth_header(token))
    assert missing_resp.status_code == 404


async def test_flag_cross_user_isolation(client: AsyncClient) -> None:
    owner_token = await signup_and_login(client, "flag-a@example.com", "flag_a")
    other_token = await signup_and_login(client, "flag-b@example.com", "flag_b")

    bill_id = (await _create_bill(client, owner_token)).json()["id"]
    flag_id = (await _create_flag(client, owner_token, bill_id)).json()["id"]

    get_resp = await client.get(
        f"/bills/{bill_id}/flags/{flag_id}", headers=auth_header(other_token)
    )
    assert get_resp.status_code == 404

    update_resp = await client.patch(
        f"/bills/{bill_id}/flags/{flag_id}",
        json={"status": "dismissed"},
        headers=auth_header(other_token),
    )
    assert update_resp.status_code == 404

    delete_resp = await client.delete(
        f"/bills/{bill_id}/flags/{flag_id}", headers=auth_header(other_token)
    )
    assert delete_resp.status_code == 404


# --- Regression: blocker #1 --------------------------------------------------------------
# POST /bills/{bill_id}/flags with only the required fields used to 500 because `status`
# was dumped as explicit `None`, overriding the model's default for the NOT NULL column.
async def test_create_flag_with_only_required_fields_succeeds(client: AsyncClient) -> None:
    token = await signup_and_login(client, "flag-minimal@example.com", "flag_minimal")
    bill_id = (await _create_bill(client, token)).json()["id"]

    response = await _create_flag(client, token, bill_id)
    assert response.status_code == 201
    assert response.json()["status"] == "open"


# --- Regression: blocker #3 --------------------------------------------------------------
# POST /bills/{bill_id}/flags used to succeed for a bill_id the caller doesn't own, as long
# as the bill existed for *someone*.
async def test_create_flag_on_other_users_bill_is_not_found(client: AsyncClient) -> None:
    owner_token = await signup_and_login(client, "flag-cross-a@example.com", "flag_cross_a")
    other_token = await signup_and_login(client, "flag-cross-b@example.com", "flag_cross_b")

    bill_id = (await _create_bill(client, owner_token)).json()["id"]

    response = await _create_flag(client, other_token, bill_id)
    assert response.status_code == 404
