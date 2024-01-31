from datasette_test import Datasette
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "config,tables,expected_html",
    (
        # No config, just one table should return that table
        ({}, ["test:a"], "/test/a"),
        # Table specified, should return that table
        ({"table": "b"}, ["test2:a", "test:a", "test:b"], "/test/b"),
        # Just database specified should return first table in that DB
        ({"database": "test2"}, ["test:a", "test2:b"], "/test2/b"),
        # Both database and table specified should return that table
        ({"table": "a", "database": "test2"}, ["test:a", "test2:a"], "/test2/a"),
    ),
)
async def test_homepage_table(config, tables, expected_html, tmpdir):
    test_db = str(tmpdir / "test.db")
    test_db2 = str(tmpdir / "test2.db")
    databases = []
    if any(t.split(":")[0] == "test" for t in tables):
        databases.append(test_db)
    if any(t.split(":")[0] == "test2" for t in tables):
        databases.append(test_db2)
    datasette = Datasette(databases, plugin_config={"datasette-homepage-table": config})
    # Now create the tables
    for table in tables:
        database_name, table_name = table.split(":")
        db = datasette.get_database(database_name)
        await db.execute_write(f"create table {table_name} (id integer primary key)")
    # Verify those tables exist
    for table in tables:
        database_name, table_name = table.split(":")
        table_response = await datasette.client.get(f"/{database_name}/{table_name}")
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
