from datasette import hookimpl, Response


async def homepage_table(datasette):
    # If configured, display the configured table
    config = datasette.plugin_config("datasette-homepage-table") or {}
    table = config.get("table")
    database = config.get("database")
    if not database:
        database = datasette.get_database().name
    if not table:
        table_names = await datasette.get_database().table_names()
        if table_names:
            table = table_names[0]
    if not table:
        return Response.text("No tables found", status=404)
    path = datasette.urls.table(database, table)
    response = await datasette.client.get(path)
    return Response.html(
        response.text, status=response.status_code, headers=response.headers
    )


@hookimpl
def register_routes(datasette):
    return [
        # Homepage is a special view
        (r"^/$", homepage_table),
    ]
