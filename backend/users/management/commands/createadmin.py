import environ
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from users.models import CustomUser

env = environ.Env()

environ.Env.read_env()

DJANGO_SUPERUSER_EMAIL = env("DJANGO_SUPERUSER_EMAIL")
DJANGO_SUPERUSER_USERNAME = env("DJANGO_SUPERUSER_USERNAME")
DJANGO_SUPERUSER_FIRSTNAME = env("DJANGO_SUPERUSER_FIRSTNAME")
DJANGO_SUPERUSER_LASTNAME = env("DJANGO_SUPERUSER_LASTNAME")
DJANGO_SUPERUSER_PASSWORD = env("DJANGO_SUPERUSER_PASSWORD")


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            CustomUser.objects.create_superuser(
                email=DJANGO_SUPERUSER_EMAIL,
                username=DJANGO_SUPERUSER_USERNAME,
                first_name=DJANGO_SUPERUSER_FIRSTNAME,
                last_name=DJANGO_SUPERUSER_LASTNAME,
                password=DJANGO_SUPERUSER_PASSWORD,
            )
            self.stdout.write(
                self.style.SUCCESS("Super User create successfully.")
            )
        except IntegrityError:
            self.stdout.write(
                self.style.ERROR("Super User is already exists.")
            )
