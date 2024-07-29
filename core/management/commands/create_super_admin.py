from django.core.management.base import BaseCommand

from core.models.user import User

BATCH_SIZE = 10000


class Command(BaseCommand):
    help = "Create a super admin"

    def add_arguments(self, parser):
        parser.add_argument("--email", type=str, required=True)
        parser.add_argument("--password", type=str, required=True)

    def handle(self, *args, **options):
        email = options["email"]
        password = options["password"]

        User.objects.create_superuser(email=email, password=password)
