import csv
from datetime import datetime
from typing import Any, Dict, Iterable
from django.core.management.base import BaseCommand, CommandError
from rest_framework import serializers
from django.db import connection

from core.models.detection import Detection, DetectionSource
from core.models.detection_data import (
    DetectionControlStatus,
    DetectionData,
    DetectionPrescriptionStatus,
    DetectionValidationStatus,
)
from core.models.detection_object import DetectionObject
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db.models.functions import Centroid


from core.models.object_type import ObjectType
from core.models.parcel import Parcel
from core.models.tile import TILE_DEFAULT_ZOOM, Tile
from core.models.tile_set import TileSet
from core.models.user import User
from core.utils.detection import get_linked_detections
from core.utils.prescription import compute_prescription
from core.utils.string import normalize
from simple_history.utils import bulk_create_with_history

PERCENTAGE_SAME_DETECTION_THRESHOLD = 0.5
USER_REVIEWER_MAIL = "user.reviewer.default.aigle@aigle.beta.gouv.fr"
INSERT_BATCH_SIZE = 1000


class DetectionRowSerializer(serializers.Serializer):
    score = serializers.FloatField()
    id = serializers.IntegerField(required=True)
    address = serializers.CharField(allow_blank=True, allow_null=True)
    object_type = serializers.CharField()
    detection_control_status = serializers.ChoiceField(
        choices=DetectionControlStatus.choices,
        required=False,
        allow_null=True,
        default=DetectionControlStatus.NOT_CONTROLLED,
    )
    detection_validation_status = serializers.ChoiceField(
        choices=DetectionValidationStatus.choices,
        required=False,
        allow_null=True,
        default=DetectionValidationStatus.DETECTED_NOT_VERIFIED,
    )
    detection_prescription_status = serializers.ChoiceField(
        choices=DetectionPrescriptionStatus.choices,
        required=False,
        allow_null=True,
    )
    detection_source = serializers.ChoiceField(
        choices=DetectionSource.choices,
        required=False,
        allow_null=True,
        default=DetectionSource.ANALYSIS,
    )
    user_reviewed = serializers.BooleanField(
        default=False,
        allow_null=True,
    )
    tile_x = serializers.IntegerField(required=False, allow_null=True)
    tile_y = serializers.IntegerField(required=False, allow_null=True)


TABLE_COLUMNS = list(DetectionRowSerializer().get_fields().keys()) + ["geometry"]


class Command(BaseCommand):
    help = "Import detections from CSV"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.start_time = datetime.now()

        all_object_types = ObjectType.objects.all()

        self.object_types_map = {
            normalize(object_type.name): object_type for object_type in all_object_types
        }
        self.user_reviewer = User.objects.get(email=USER_REVIEWER_MAIL)

        self.detection_objects_to_insert = []
        self.detection_datas_to_insert = []
        self.detections_to_insert = []

        self.total_inserted_detections = 0

        self.file = None
        self.total = None
        self.query_colums = None

    def add_arguments(self, parser):
        parser.add_argument("--tile-set-id", type=int, required=True)
        parser.add_argument("--batch-id", type=str)
        parser.add_argument("--file-path", type=str)
        parser.add_argument("--table-name", type=str)
        parser.add_argument("--table-schema", type=str, default="import_detections")

    def validate_arguments(self, options):
        if not options.get("file_path") and not options.get("table_name"):
            raise CommandError(
                "You have to provide either a file path or a table name with parameter --file-path or --table-name"
            )

        if options.get("table_name") and not options.get("batch_id"):
            raise CommandError(
                "You have to provide a batch id with parameter --batch-id when using a table name with parameter --table-name"
            )

        if options.get("file_path") and options.get("table_name"):
            raise CommandError(
                "You can't provide both a file path and a table name with parameter --file-path or --table-name"
            )

    def get_detection_rows_to_insert_from_file(
        self, file_path: str
    ) -> Iterable[Dict[str, Any]]:
        self.file = open(file_path, "r")
        reader = csv.DictReader(self.file, delimiter=";", quotechar='"')
        return reader

    def get_detection_rows_to_insert_from_table(
        self, table_name: str, table_schema: str, batch_id: str
    ) -> Iterable[Dict[str, Any]]:
        self.cursor = connection.cursor()
        self.cursor.execute(
            "SELECT count(*) FROM %s.%s WHERE batch_id = %s"
            % (table_schema, table_name, f"'{batch_id}'")
        )
        self.total = self.cursor.fetchone()[0]
        self.cursor.execute(
            "SELECT %s FROM %s.%s WHERE batch_id = %s ORDER BY score DESC"
            % (", ".join(TABLE_COLUMNS), table_schema, table_name, f"'{batch_id}'")
        )
        return map(lambda row: dict(zip(TABLE_COLUMNS, row)), self.cursor)

    def handle(self, *args, **options):
        self.validate_arguments(options)

        tile_set_id = options["tile_set_id"]
        self.batch_id = options.get("batch_id") or datetime.now().strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        print(f"Starting importing detections for batch: {self.batch_id}")

        self.tile_set = TileSet.objects.get(id=tile_set_id)
        self.tile_set.last_import_started_at = self.start_time
        self.tile_set.last_import_ended_at = None
        self.tile_set.save()

        print(f"TileSet found: {self.tile_set.name}")

        if options.get("file_path"):
            detection_rows_to_insert = self.get_detection_rows_to_insert_from_file(
                file_path=options["file_path"]
            )
        else:
            detection_rows_to_insert = self.get_detection_rows_to_insert_from_table(
                table_name=options["table_name"],
                table_schema=options["table_schema"],
                batch_id=self.batch_id,
            )

        for row in detection_rows_to_insert:
            self.queue_detection(row)
            self.insert_detections()

        if self.file:
            self.file.close()

        if self.cursor:
            self.cursor.close()

        self.insert_detections(force=True)
        self.tile_set.last_import_ended_at = datetime.now()
        self.tile_set.save()

        print(f"Detections import finished for batch: {self.batch_id}")

    def queue_detection(self, detection_row: Dict[str, Any]):
        # validate input data

        geometry_raw = detection_row.pop("geometry")

        if not geometry_raw:
            raise CommandError("Missing geometry for detection")

        object_type_raw = detection_row.get("object_type", None)

        if not object_type_raw:
            raise CommandError("Missing object type for detection")

        object_type = self.object_types_map[object_type_raw]

        if not object_type:
            raise CommandError(f"Unknown object type: {object_type_raw}")

        geometry = GEOSGeometry(geometry_raw, srid=4326)

        serializer = DetectionRowSerializer(data=detection_row)
        if not serializer.is_valid():
            print(
                f"Invalid detection row: {detection_row}, errors: {
                    serializer.errors} skipping..."
            )
            return

        serialized_detection = serializer.validated_data

        # WE DO NOT FILTER OUT DETECTIONS THAT ARE NOT IN THE SAME TILE SET ANYMORE

        # # get linked detections

        # # linked detections in the ones to insert

        # linked_detections_to_insert = [
        #     detection
        #     for detection in self.detections_to_insert
        #     if detection.geometry.intersects(geometry)
        #     and detection.detection_object.object_type == object_type
        # ]
        # if linked_detections_to_insert:
        #     for linked_detection in linked_detections_to_insert:
        #         if (
        #             geometry.intersection(linked_detection.geometry).area
        #             > geometry.area * PERCENTAGE_SAME_DETECTION_THRESHOLD
        #             or linked_detection.geometry.intersection(geometry).area
        #             > geometry.area * PERCENTAGE_SAME_DETECTION_THRESHOLD
        #         ):
        #             print(f"Detection already exists in tileset {
        #                   self.tile_set.name} and is going to be inserted. Skipping...")
        #             return

        # linked detections already in the database

        # we filter out detections that have too small intersection area with the detection
        linked_detections = get_linked_detections(
            detection_geometry=geometry,
            object_type_id=object_type.id,
            exclude_tile_set_ids=[self.tile_set.id],
        )

        # WE DO NOT FILTER OUT DETECTIONS THAT ARE NOT IN THE SAME TILE SET ANYMORE

        # # deal with linked detections

        # linked_detection_same_tileset = next(
        #     (
        #         detection
        #         for detection in linked_detections
        #         if detection.tile_set.id == self.tile_set.id
        #     ),
        #     None,
        # )

        # if linked_detection_same_tileset:
        #     print(f"Detection already exists in tileset {self.tile_set.name}, id: {
        #           linked_detection_same_tileset.id}. Skipping...")
        #     return

        # create detection

        centroid = Centroid(geometry)
        tile = Tile.objects.filter(
            geometry__contains=centroid, z=TILE_DEFAULT_ZOOM
        ).first()

        if not tile:
            if serialized_detection.get("tile_x") and serialized_detection.get(
                "tile_y"
            ):
                tile = Tile.objects.filter(
                    x=serialized_detection["tile_x"],
                    y=serialized_detection["tile_y"],
                    z=TILE_DEFAULT_ZOOM,
                ).first()

                if not tile:
                    tile = Tile.objects.create(
                        x=serialized_detection["tile_x"],
                        y=serialized_detection["tile_y"],
                        z=TILE_DEFAULT_ZOOM,
                    )
            else:
                print("Tile not found for detection, skipping...")
                return

        # detection data

        detection_data = DetectionData(
            detection_control_status=serialized_detection["detection_control_status"],
            detection_validation_status=serialized_detection[
                "detection_validation_status"
            ],
            detection_prescription_status=serialized_detection[
                "detection_prescription_status"
            ],
        )

        if serialized_detection["user_reviewed"]:
            detection_data.user_last_update = self.user_reviewer

        # detection object

        if linked_detections:
            linked_detection = linked_detections[0]
            detection_object = linked_detection.detection_object

            if not detection_object.address and serialized_detection["address"]:
                detection_object.address = serialized_detection["address"]
                detection_object.save()

            if not detection_data.detection_control_status:
                detection_data.detection_control_status = (
                    linked_detection.detection_data.detection_control_status
                )

            if not detection_data.detection_validation_status:
                detection_data.detection_validation_status = (
                    linked_detection.detection_data.detection_validation_status
                )
        else:
            parcel = Parcel.objects.filter(geometry__contains=centroid).first()
            detection_object = DetectionObject(
                object_type=object_type,
                parcel=parcel,
                address=serialized_detection["address"],
                batch_id=self.batch_id,
                import_id=serialized_detection["id"],
            )
            self.detection_objects_to_insert.append(detection_object)

            if not detection_data.detection_control_status:
                detection_data.detection_control_status = (
                    DetectionControlStatus.NOT_CONTROLLED
                )

            if not detection_data.detection_validation_status:
                detection_data.detection_validation_status = (
                    DetectionValidationStatus.DETECTED_NOT_VERIFIED
                )

        # detection

        detection = Detection(
            geometry=geometry,
            score=serialized_detection["score"],
            detection_source=serialized_detection["detection_source"]
            or DetectionSource.ANALYSIS,
            auto_prescribed=False,
            tile=tile,
            tile_set=self.tile_set,
            detection_data=detection_data,
            batch_id=self.batch_id,
            import_id=serialized_detection["id"],
        )

        detection.detection_object = detection_object

        self.detection_datas_to_insert.append(detection_data)
        self.detections_to_insert.append(detection)

    def insert_detections(self, force=False):
        if (
            not force
            and len(self.detections_to_insert) < INSERT_BATCH_SIZE
            and len(self.detection_datas_to_insert) < INSERT_BATCH_SIZE
            and len(self.detection_objects_to_insert) < INSERT_BATCH_SIZE
        ):
            return

        print(f"Inserting {len(self.detections_to_insert)} detections")

        bulk_create_with_history(self.detection_objects_to_insert, DetectionObject)
        bulk_create_with_history(self.detection_datas_to_insert, DetectionData)
        bulk_create_with_history(self.detections_to_insert, Detection)

        detection_objects = [
            detection.detection_object for detection in self.detections_to_insert
        ]

        for detection_object in detection_objects:
            compute_prescription(detection_object)

        self.total_inserted_detections += len(self.detections_to_insert)

        if self.total:
            print(
                f"Inserted {
                    self.total_inserted_detections}/{self.total} detections in total"
            )
        else:
            print(f"Inserted {
                  self.total_inserted_detections} detections in total")

        print(f"Elapsed time: {datetime.now() - self.start_time}")

        self.detection_objects_to_insert = []
        self.detection_datas_to_insert = []
        self.detections_to_insert = []
