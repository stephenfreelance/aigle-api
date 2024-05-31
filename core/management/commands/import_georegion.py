import json
from typing import TypedDict
from django.core.management.base import BaseCommand, CommandError
import shapefile

from core.management.commands._common.file import download_file, extract_zip
from core.models import GeoRegion
from core.utils.string import normalize
from django.contrib.gis.geos import GEOSGeometry

SHP_ZIP_URL = 'https://osm13.openstreetmap.fr/~cquest/openfla/export/regions-20180101-shp.zip'
SHP_FILE_NAME = 'regions-20180101.shp'

class RegionProperties(TypedDict):
    code_insee: str
    nom: str
    nuts2: str
    surf_km2: int
    wikipedia: str


class Command(BaseCommand):
    help = "Import regions to database from SHP"

    def handle(self, *args, **options):
        temp_dir, file_path = download_file(url=SHP_ZIP_URL, file_name='regions.zip')

        extract_folder_path = f'{temp_dir.name}/out'
        extract_zip(file_path=file_path, output_dir=extract_folder_path)

        shape = shapefile.Reader(f"{extract_folder_path}/{SHP_FILE_NAME}")

        regions = []

        for feature in shape.shapeRecords():
            properties: RegionProperties = feature.__geo_interface__["properties"]
            geometry = GEOSGeometry(json.dumps(feature.__geo_interface__['geometry']))
            
            regions.append(
                GeoRegion(
                    name=normalize(properties['nom']),
                    display_name=properties['nom'],
                    insee_code=properties['code_insee'],
                    surface_km2=properties['surf_km2'],
                    geometry=geometry
                )
            )

        GeoRegion.objects.bulk_create(
            regions
        )


        temp_dir.cleanup()
