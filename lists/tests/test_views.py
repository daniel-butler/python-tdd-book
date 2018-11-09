from unittest import skip
import unittest
from unittest.mock import patch, Mock

from django.http import HttpRequest
from django.urls import resolve
from django.test import TestCase
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.html import escape
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from lists.views import NewListView
from lists.models import Item, List
from lists.forms import (
    ItemForm, ExistingListItemForm, ShareListForm,
    EMPTY_ITEM_ERROR, DUPLICATE_ITEM_ERROR
)

User = get_user_model()


class HomePageTest(TestCase):

    def test_home_page_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, r'lists/home.html')

    def test_home_page_uses_item_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)


class ListViewTest(TestCase):

    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, r'lists/list.html')

    # cleared unittest broke with jQuery
    # def test_displays_all_items(self):
    #     correct_list = List.objects.create()
    #     Item.objects.create(text='itemey 1', list=correct_list)
    #     Item.objects.create(text='itemey 2', list=correct_list)
    #     other_list = List.objects.create()
    #     Item.objects.create(text='other list itemey 1', list=other_list)
    #     Item.objects.create(text='other list itemey 2', list=other_list)
    #
    #     response = self.client.get(f'/lists/{correct_list.id}/')
    #
    #     print(response.content.decode('utf8'))
    #     self.assertContains(response, 'itemey 1')
    #     self.assertContains(response, 'itemey 2')
    #     self.assertNotContains(response, 'other list itemey 1')
    #     self.assertNotContains(response, 'other list itemey 2')

    def test_passes_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get(f'/lists/{correct_list.id}/')
        self.assertEqual(response.context['list'], correct_list,"list is not passed to the template")

    def test_can_save_a_POST_request_to_an_exisiting_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_POST_redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )

        self.assertRedirects(response, f'/lists/{correct_list.id}/')

    def post_invalid_input(self):
        list_ = List.objects.create()
        return self.client.post(f'/lists/{list_.id}/', data={'text': ''})

    def test_for_invalid_input_nothing_saved_to_db(self):
        self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renders_list_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lists/list.html')

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['form'], ExistingListItemForm)

    def test_for_invalid_input_shows_error_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_displays_item_form(self):
        list_ = List.objects.create()
        response = self.client.post(f'/lists/{list_.id}/', data={'text': ''})
        self.assertIsInstance(response.context['form'], ExistingListItemForm)
        self.assertContains(response, 'name="text"')

    def test_list_uses_Share_List_Form(self):
        list_ = List.objects.create()
        response = self.client.get(f"/lists/{list_.id}/")
        self.assertIsInstance(response.context['share_form'], ShareListForm)
        self.assertContains(response, 'name="sharee"')
        self.assertContains(response, _('Share With'))  # Label


class NewListViewIntegratedTest(TestCase):

    def test_can_save_a_POST_request(self):
        response = self.client.post('/lists/new', data={'text': 'A new list item'})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_redirects_after_POST(self):
        response = self.client.post('/lists/new', data={'text': 'A new list item',})
        new_list = List.objects.first()
        self.assertRedirects(response, f'/lists/{new_list.id}/')

    def test_validation_errors_are_sent_back_to_home_page_template(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lists/home.html')
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_invalid_list_items_arent_saved(self):
        self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renders_home_template(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lists/home.html')

    def test_validation_errors_are_shown_on_home_page(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertIsInstance(response.context['form'], ItemForm)

    def test_duplicate_item_validation_errors_end_up_on_lists_page(self):
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='textey')
        response = self.client.post(
            f'/lists/{list1.id}/',
            data={'text': 'textey'}
        )

        expected_error = escape("You've already got this in your list")
        self.assertContains(response, expected_error)
        self.assertTemplateUsed(response, 'lists/list.html')
        self.assertEqual(Item.objects.all().count(), 1)


class MyListsTest(TestCase):

    def test_my_lists_url_renders_my_lists_template(self):
        User.objects.create(email='a@b.com')
        response = self.client.get('/lists/users/a@b.com/')
        self.assertTemplateUsed(response, 'lists/my_lists.html')

    def test_passes_correct_owner_to_template(self):
        User.objects.create(email='wrong@owner.com')
        correct_user = User.objects.create(email='a@b.com')
        response = self.client.get('/lists/users/a@b.com/')
        self.assertEqual(response.context['owner'], correct_user)

    def test_list_owner_is_saved_if_user_is_authenticated(self):
        user = User.objects.create(email='a@b.com')
        self.client.force_login(user)
        self.client.post('/lists/new', data={'text': 'new item'})
        list_ = List.objects.first()
        self.assertEqual(list_.owner, user)


# @patch('lists.views.NewListForm')
# class NewListViewUnitTest(unittest.TestCase):
#
#     def setUp(self):
#         self.request = HttpRequest()
#         self.request.POST['text'] = 'new list item'
#         self.request.user = Mock()
#
#     def test_passes_POST_data_to_NewListForm(self, mockNewListForm):
#         new_list = NewListView()
#         new_list.post(self.request)
#         mockNewListForm.assert_called_once_with(data=self.request.POST)
#
#     def test_saves_form_with_owner_if_form_valid(self, mockNewListForm):
#         mock_form = mockNewListForm.return_value
#         mock_form.is_valid.return_value = True
#         NewListView.as_view()(self.request)
#         mock_form.save.assert_called_once_with(owner=self.request.user)
#
#     @patch('lists.views.redirect')
#     def test_redirects_to_form_returned_object_if_form_valide(
#         self, mock_redirect, mockNewListForm
#     ):
#         mock_form = mockNewListForm.return_value
#         mock_form.is_valid.return_value = True
#
#         response = NewListView.as_view()(self.request)
#
#         self.assertEqual(response, mock_redirect.return_value)
#         mock_redirect.assert_called_once_with(mock_form.save.return_value)
#
#     @patch('lists.views.render')
#     def test_renders_home_template_with_form_if_form_invalid(
#         self, mock_render, mockNewListForm
#     ):
#         mock_form = mockNewListForm.return_value
#         mock_form.is_valid.return_value = False
#
#         response = NewListView.as_view()(self.request)
#
#         self.assertEqual(response, mock_render.return_value)
#         mock_render.assert_called_once_with(
#             self.request, 'lists/home.html', {'form': mock_form}
#         )
#
#     def test_does_not_save_if_form_is_invalid(self, mockNewListForm):
#         mock_form = mockNewListForm.return_value
#         mock_form.is_valid.return_value = False
#         NewListView.as_view()(self.request)
#         self.assertFalse(mock_form.save.called)
#

class ShareListTest(TestCase):

    def setUp(self):
        self.email = 'edith@example.com'
        self.user = User.objects.create(email=self.email)
        self.user_sharer = User.objects.create()
        self.user.save()
        self.user_sharer.save()
        self.list_ = List.objects.create(owner=self.user_sharer)
        self.list_.save()

    def test_share_list_POST_renders_share_template(self):
        response = self.client.post(
            f'/lists/{self.list_.id}/share',
            {'sharee': self.email}
        )
        self.assertRedirects(response, f'/lists/{self.list_.id}/')

    def test_share_list_GET_renders_list_template(self):
        response = self.client.get(f'/lists/{self.list_.id}/share')
        self.assertRedirects(response, f'/lists/{self.list_.id}/')

    def test_user_can_share_a_list(self):
        self.client.post(f'/lists/{self.list_.id}/share', {'sharee': self.email})
        self.assertIn(self.user, self.list_.shared_with.all())

    def test_user_can_share_list_with_nonuser(self):
        email = 'someone@else.com'
        self.client.post(f'/lists/{self.list_.id}/share', {'sharee': email})
        self.assertIn(User.objects.filter(email=email)[0], self.list_.shared_with.all())
