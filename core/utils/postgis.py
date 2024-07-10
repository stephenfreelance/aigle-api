from django.db import connection
from django.db.models import Func, CharField, TextChoices


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


class GeometryType(TextChoices):
    POINT = "POINT"
    LINESTRING = "LINESTRING"
    POLYGON = "POLYGON"
    MULTIPOINT = "MULTIPOINT"
    MULTILINESTRING = "MULTILINESTRING"
    MULTIPOLYGON = "MULTIPOLYGON"
    GEOMETRYCOLLECTION = "GEOMETRYCOLLECTION"
    CIRCULARSTRING = "CIRCULARSTRING"
    COMPOUNDCURVE = "COMPOUNDCURVE"
    CURVEPOLYGON = "CURVEPOLYGON"
    MULTICURVE = "MULTICURVE"
    MULTISURFACE = "MULTISURFACE"
    POLYHEDRALSURFACE = "POLYHEDRALSURFACE"
    TRIANGLE = "TRIANGLE"
    TIN = "TIN"


class GetGeometryType(Func):
    function = "GeometryType"
    output_field = CharField(
        choices=GeometryType.choices,
    )
