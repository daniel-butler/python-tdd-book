from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string


class Command(BaseCommand):
    help = 'Generates a django secret key'

    def __init__(self):
        super().__init__(no_color=True)

    def handle(self, *args, **options):
        return get_random_string(50)

