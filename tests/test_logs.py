from datetime import datetime


def test_create_and_get_log(client):
    payload = {"severity": "INFO", "source": "test", "message": "hello"}
    r = client.post("/api/v1/logs/", json=payload)
    assert r.status_code == 201
    created = r.json()["data"]["log"]

    log_id = created["id"]
    r2 = client.get(f"/api/v1/logs/{log_id}")
    assert r2.status_code == 200
    fetched = r2.json()["data"]["log"]
    assert fetched["message"] == "hello"


def test_list_and_aggregate(client):
    client.post("/api/v1/logs/", json={"severity": "INFO", "source": "app", "message": "m1"})
    client.post("/api/v1/logs/", json={"severity": "ERROR", "source": "app", "message": "m2"})

    r = client.get("/api/v1/logs/?limit=10&offset=0")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] >= 2

    r2 = client.get("/api/v1/logs/aggregate/by/severity")
    assert r2.status_code == 200
    buckets = r2.json()["data"]["aggregation"]["buckets"]
    assert isinstance(buckets, list)


def test_update_and_delete(client):
    r = client.post("/api/v1/logs/", json={"severity": "INFO", "source": "test", "message": "x"})
    log_id = r.json()["data"]["log"]["id"]

    r2 = client.patch(f"/api/v1/logs/{log_id}", json={"message": "y"})
    assert r2.status_code == 200
    assert r2.json()["data"]["log"]["message"] == "y"

    r3 = client.delete(f"/api/v1/logs/{log_id}")
    assert r3.status_code == 200
    r4 = client.get(f"/api/v1/logs/{log_id}")
    assert r4.status_code == 404

