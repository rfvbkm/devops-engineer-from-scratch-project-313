from fastapi.testclient import TestClient


def test_list_links_empty(client: TestClient) -> None:
    r = client.get("/api/links")
    assert r.status_code == 200
    assert r.json() == []


def test_create_link_201(client: TestClient) -> None:
    body = {
        "original_url": "https://example.com/long-url",
        "short_name": "exmpl",
    }
    r = client.post("/api/links", json=body)
    assert r.status_code == 201
    data = r.json()
    assert data["id"] == 1
    assert data["original_url"] == body["original_url"]
    assert data["short_name"] == body["short_name"]
    assert data["short_url"] == "https://short.io/r/exmpl"


def test_create_duplicate_409(client: TestClient) -> None:
    body = {
        "original_url": "https://example.com/a",
        "short_name": "dup",
    }
    assert client.post("/api/links", json=body).status_code == 201
    r = client.post("/api/links", json=body)
    assert r.status_code == 409
    assert r.json() == {"detail": "Short name already exists"}


def test_list_links_after_create(client: TestClient) -> None:
    client.post(
        "/api/links",
        json={
            "original_url": "https://example.com/long-url",
            "short_name": "exmpl",
        },
    )
    r = client.get("/api/links")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["short_url"] == "https://short.io/r/exmpl"


def test_get_link_by_id_200(client: TestClient) -> None:
    created = client.post(
        "/api/links",
        json={
            "original_url": "https://example.com/long-url",
            "short_name": "exmpl",
        },
    ).json()
    r = client.get(f"/api/links/{created['id']}")
    assert r.status_code == 200
    assert r.json() == created


def test_get_link_404(client: TestClient) -> None:
    r = client.get("/api/links/999")
    assert r.status_code == 404
    assert r.json() == {"detail": "Link not found"}


def test_put_link_200(client: TestClient) -> None:
    created = client.post(
        "/api/links",
        json={
            "original_url": "https://example.com/old",
            "short_name": "old",
        },
    ).json()
    body = {
        "original_url": "https://example.com/new",
        "short_name": "new",
    }
    r = client.put(f"/api/links/{created['id']}", json=body)
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == created["id"]
    assert data["original_url"] == body["original_url"]
    assert data["short_name"] == body["short_name"]
    assert data["short_url"] == "https://short.io/r/new"


def test_put_link_404(client: TestClient) -> None:
    r = client.put(
        "/api/links/42",
        json={
            "original_url": "https://example.com/x",
            "short_name": "x",
        },
    )
    assert r.status_code == 404
    assert r.json() == {"detail": "Link not found"}


def test_put_link_conflict_409(client: TestClient) -> None:
    client.post(
        "/api/links",
        json={"original_url": "https://a.com", "short_name": "a"},
    )
    b = client.post(
        "/api/links",
        json={"original_url": "https://b.com", "short_name": "b"},
    ).json()
    r = client.put(
        f"/api/links/{b['id']}",
        json={"original_url": "https://b.com", "short_name": "a"},
    )
    assert r.status_code == 409
    assert r.json() == {"detail": "Short name already exists"}


def test_delete_link_204(client: TestClient) -> None:
    created = client.post(
        "/api/links",
        json={"original_url": "https://x.com", "short_name": "x"},
    ).json()
    r = client.delete(f"/api/links/{created['id']}")
    assert r.status_code == 204
    assert r.content == b""


def test_delete_link_404(client: TestClient) -> None:
    r = client.delete("/api/links/999")
    assert r.status_code == 404
    assert r.json() == {"detail": "Link not found"}
