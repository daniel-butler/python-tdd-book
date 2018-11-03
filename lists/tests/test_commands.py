from unittest import TestCase

from lists.management.commands.generate_key import Command


class CommandTestCase(TestCase):

    def test_django_secret_key_generated(self):
        c = Command()
        key = c.execute(no_color=True)
        self.assertEqual(str, type(key))
        self.assertEqual(50, len(key))
