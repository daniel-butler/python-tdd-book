import unittest

from selenium import webdriver


class NewVistorTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_start_a_list_and_retrieve_it_later(self):
        # Edit has heard about a cool new online to-do app. She goes to check out its
        # homepage
        self.browser.get("http://localhost:8000")

        # She notices the page title and header mention to-do lists
        self.assertIn('To-Do', self.browser.title)
        self.fail('Finish the test!')

        # She is invited to enter a to-do item straight away

        # She types "Buy peacock feathers" into a text box (Edithi's hobby is tying
        # fly-fishing lures)

        # When she hits enter, the page updates, and now the page lists
        # "1: Buy peacock feathers" as an item in a to-do lists

        # There is still a text box inviting her to add another item. She enteres
        # "Use peacock feathers to make a fly" (Edith is very methodical)

        # The page updates again, and now shows both items on her lists

        # Edit wonders whether the site will remember her list. Then she sees that the
        # site has generated a unique URL for her -- there is some explanatory text
        # to that effect.

        # She visits that URL - her to-do list is still there.

        # Statisfied, she goes back to sleep


if __name__ == '__main__':
    unittest.main()
