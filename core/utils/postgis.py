from django.db import connection


def ST_TileEnvelope(z: int, x: int, y: int):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT 
                ST_AsText(
                    ST_Transform(
                       ST_TileEnvelope(%s, %s, %s), 
                       4326
                    )
                )
        """,
            [z, x, y],
        )
        row = cursor.fetchone()
        return row[0] if row else None
