from selenium.common.exceptions import NoSuchElementException
from .base import FunctionalTest
from .list_page import ListPage


class OwnerTest(FunctionalTest):

    def test_no_list_owner(self):
        # Eric goes to the awesome list webpage and starts a new list
        # He starts with the biggests things on his to-do list to make sure it is
        # working
        self.browser.get(self.live_server_url)
        response = self.add_list_item('Wake up tomorrow')

        # He notices that the shared with section is blank
        list_page = ListPage(self)
        labels = self.browser.find_elements_by_tag_name('label')
        self.assertIn('Shared With:', [label.text for label in labels])
        try:
            list_page.get_list_owner()
        except NoSuchElementException as e:
            pass  # Should not be able to find the element
