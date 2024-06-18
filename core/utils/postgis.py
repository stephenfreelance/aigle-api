from django.db import connection


def ST_TileEnvelope(z, x, y):
    with connection.cursor() as cursor:
        cursor.execute("SELECT ST_AsText(ST_TileEnvelope(%s, %s, %s))", [z, x, y])
        row = cursor.fetchone()
        return row[0] if row else None
