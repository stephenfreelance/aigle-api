import json
from typing import TypedDict
from django.core.management.base import BaseCommand
import shapefile
from pyproj import Transformer

from core.management.commands._common.file import download_file, extract_zip
from core.models import GeoRegion
from core.utils.string import normalize
from django.contrib.gis.geos import GEOSGeometry

SHP_ZIP_URL = (
    "https://osm13.openstreetmap.fr/~cquest/openfla/export/regions-20180101-shp.zip"
)
SHP_FILE_NAME = "regions-20180101.shp"


class RegionProperties(TypedDict):
    code_insee: str
    nom: str
    nuts2: str
    surf_km2: int
    wikipedia: str


class Command(BaseCommand):
    help = "Import regions to database from SHP"

    def handle(self, *args, **options):
        temp_dir, file_path = download_file(url=SHP_ZIP_URL, file_name="regions.zip")

        extract_folder_path = f"{temp_dir.name}/out"
        extract_zip(file_path=file_path, output_dir=extract_folder_path)

        shape = shapefile.Reader(f"{extract_folder_path}/{SHP_FILE_NAME}")

        # Define input and output CRS
        input_crs = "epsg:2154"  # Adjust based on the CRS of the shapefile
        output_crs = "epsg:4326"
        transformer = Transformer.from_crs(input_crs, output_crs, always_xy=True)

        regions = []

        for feature in shape.shapeRecords():
            properties: RegionProperties = feature.__geo_interface__["properties"]
            geometry = feature.__geo_interface__["geometry"]

            # Transform the geometry coordinates
            transformed_coords = []
            if geometry["type"] == "Polygon":
                for ring in geometry["coordinates"]:
                    transformed_ring = [transformer.transform(x, y) for x, y in ring]
                    transformed_coords.append(transformed_ring)
            elif geometry["type"] == "MultiPolygon":
                for polygon in geometry["coordinates"]:
                    transformed_polygon = []
                    for ring in polygon:
                        transformed_ring = [
                            transformer.transform(x, y) for x, y in ring
                        ]
                        transformed_polygon.append(transformed_ring)
                    transformed_coords.append(transformed_polygon)

            # Create the transformed geometry
            transformed_geometry = {
                "type": geometry["type"],
                "coordinates": transformed_coords,
            }

            geom = GEOSGeometry(json.dumps(transformed_geometry))

            regions.append(
                GeoRegion(
                    name="new_" + normalize(properties["nom"]),
                    display_name="new_" + properties["nom"],
                    insee_code="new_" + properties["code_insee"],
                    surface_km2=properties["surf_km2"],
                    geometry=geom,
                )
            )

        GeoRegion.objects.bulk_create(regions)

        temp_dir.cleanup()
