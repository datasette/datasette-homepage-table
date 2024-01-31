from datasette import hookimpl, Response, Request
from datasette.views.index import IndexView


async def homepage_table(datasette, scope, receive):
    # If configured, display the configured table
    config = datasette.plugin_config("datasette-homepage-table") or {}
    table = config.get("table")
    database = config.get("database")
    if not database:
        database = datasette.get_database().name
    if not table:
        table_names = await datasette.get_database(database).table_names()
        if table_names:
            table = table_names[0]
    if table:
        path = datasette.urls.table(database, table)
    else:
        homepage_view = IndexView(datasette)
        scope = dict(scope, url_route={"kwargs": {"format": ""}})
        return await homepage_view.get(Request(scope, receive))

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
