from datasette_test import Datasette
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "config,expected_html",
    (
        ({}, "/test/a"),
        ({"table": "b"}, "/test/b"),
        ({"table": "a"}, "/test/a"),
        ({"table": "a", "database": "test"}, "/test/a"),
    ),
)
async def test_homepage_table(config, expected_html, tmpdir):
    test_db = str(tmpdir / "test.db")
    datasette = Datasette([test_db], plugin_config={"datasette-homepage-table": config})
    db = datasette.get_database("test")
    await db.execute_write("create table a (id integer primary key)")
    await db.execute_write("create table b (id integer primary key)")
    table_response = await datasette.client.get("/test/a")
    assert table_response.status_code == 200
    # Now try the homepage
    response = await datasette.client.get("/")
    assert response.status_code == 200
    assert expected_html in response.text


@pytest.mark.asyncio
async def test_homepage_if_no_tables():
    datasette = Datasette(memory=True)
    response = await datasette.client.get("/")
    assert response.status_code == 200
    assert "index.html" in response.text
