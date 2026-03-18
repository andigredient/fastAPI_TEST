import pytest

@pytest.mark.asyncio
async def test_create_and_get(client):
    resp = await client.post("/links/shorten", json={"original_url": "https://test.com"})
    code = resp.json()
    assert resp.status_code == 200    
    resp = await client.get(f"/{code}", follow_redirects=False)
    assert resp.status_code in [302, 307]

@pytest.mark.asyncio
async def test_custom_alias(client):
    resp = await client.post("/links/shorten", json={
        "original_url": "https://test.com",
        "custom_alias": "mytest"
    })
    assert resp.json() == "mytest"

@pytest.mark.asyncio
async def test_stats(client):
    await client.post("/links/shorten", json={"original_url": "https://test.com", "custom_alias": "stats"})
    resp = await client.get("/links/stats/stats")
    assert resp.status_code == 200
    assert resp.json()["clicks"] == 0

@pytest.mark.asyncio
async def test_delete(client):
    await client.post("/links/shorten", json={"original_url": "https://test.com", "custom_alias": "del"})
    await client.delete("/links/del")
    resp = await client.get("/del", follow_redirects=False)
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_update(client):
    await client.post("/links/shorten", json={"original_url": "https://test.com", "custom_alias": "old"})
    await client.put("/links/old", json={"new_code": "new"})
    assert (await client.get("/old", follow_redirects=False)).status_code == 404
    assert (await client.get("/new", follow_redirects=False)).status_code in [302, 307]

@pytest.mark.asyncio
async def test_search(client):
    await client.post("/links/shorten", json={"original_url": "https://test.com", "custom_alias": "findme"})
    resp = await client.get("/links/search", params={"original_url": "https://test.com"})
    assert "findme" in resp.json()["result"]