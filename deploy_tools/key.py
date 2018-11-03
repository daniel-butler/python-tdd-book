from jinja2 import Environment, FileSystemLoader
from django.utils.crypto import get_random_string


def create_django_secret_key():
    return get_random_string(50)


env = Environment(loader=FileSystemLoader('/'))
env.globals['create_django_secret_key'] = create_django_secret_key
