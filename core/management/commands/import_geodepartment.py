import json
from typing import List, TypedDict
from django.core.management.base import BaseCommand, CommandError
import shapefile

from core.management.commands._common.file import (
    download_file,
    download_json,
    extract_zip,
)
from core.models import GeoRegion
from core.models.geo_department import GeoDepartment
from core.utils.string import normalize
from django.contrib.gis.geos import GEOSGeometry

SHP_ZIP_URL = (
    "http://osm13.openstreetmap.fr/~cquest/openfla/export/departements-20180101-shp.zip"
)
SHP_FILE_NAME = "departements-20180101.shp"

ADDITIONAL_JSON_URL = (
    "https://www.data.gouv.fr/fr/datasets/r/7b4bc207-4e66-49d2-b1a5-26653e369b66"
)


class RegionProperties(TypedDict):
    code_insee: str
    nom: str
    nuts3: str
    surf_km2: int
    wikipedia: str


class AdditionalInfos(TypedDict):
    num_dep: str
    dep_name: str
    region_name: str


class Command(BaseCommand):
    help = "Import departments to database from SHP"

    def handle(self, *args, **options):
        # shape data
        temp_dir, file_path = download_file(url=SHP_ZIP_URL, file_name="regions.zip")

        extract_folder_path = f"{temp_dir.name}/out"
        extract_zip(file_path=file_path, output_dir=extract_folder_path)

        shape = shapefile.Reader(f"{extract_folder_path}/{SHP_FILE_NAME}")

        # additional data
        additional_data: List[AdditionalInfos] = download_json(url=ADDITIONAL_JSON_URL)

        regions = GeoRegion.objects.filter(
            name__in=[normalize(data["region_name"]) for data in additional_data]
        ).all()

        region_name_region_map = {region.name: region for region in regions}

        department_numero_region_map = {}
        for data_item in additional_data:
            region = region_name_region_map.get(normalize(data_item["region_name"]))

            if not region:
                raise CommandError(
                    f'Region was not found in database: {data_item['region_name']}. Did you import regions?'
                )

            department_numero_region_map[str(data_item["num_dep"])] = region

        departments = []

        for feature in shape.shapeRecords():
            properties: RegionProperties = feature.__geo_interface__["properties"]
            geometry = GEOSGeometry(json.dumps(feature.__geo_interface__["geometry"]))

            # special case for 69
            code_insee_simplified = (
                "69"
                if properties["code_insee"].startswith("69")
                else properties["code_insee"]
            )

            department = GeoDepartment(
                name=properties["nom"],
                insee_code=properties["code_insee"],
                surface_km2=properties["surf_km2"],
                geometry=geometry,
                region=department_numero_region_map[code_insee_simplified],
            )

            departments.append(department)

        GeoDepartment.objects.bulk_create(departments)

        temp_dir.cleanup()
