from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Fill Data Base with the test data"

    def handle(self, *args, **kwargs):
        print("Hello")
