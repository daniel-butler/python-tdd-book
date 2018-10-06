from selenium import webdriver
from .base import FunctionalTest


def quit_if_possible(browser):
    try: browser.quit()
    except: pass


class SharingTest(FunctionalTest):

    def test_can_share_a_list_with_another_user(self):
        # Edit is a logged in user
        self.create_pre_authenticated_session('edith@example.com')
        edith_browser = self.browser
        self.addCleanup(lambda: quit_if_possible(edith_browser))

        # Her friend Oniciferous is also hanging out on the lists site
        oni_broswer = webdriver.Firefox()
        self.addCleanup(lambda: quit_if_possible(oni_broswer))
        self.browser = oni_broswer
        self.create_pre_authenticated_session('oniciferous@example.com')

        # Edith goes to the home page and starts a list
        self.browser = edith_browser
        self.browser.get(self.live_server_url)
        self.add_list_item('Get help')

        # She notices a "Share this list" option
        share_box = self.browser.find_element_by_css_selector(
            'input[name=sharee]'
        )
        self.assertEqual(
            share_box.get_attribute('placeholder'),
            'your-friend@example.com'
        )
