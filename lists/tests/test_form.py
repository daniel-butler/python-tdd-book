import unittest
from unittest.mock import patch, Mock

from django.test import TestCase
from django.contrib.auth import get_user_model

from lists.forms import (
    DUPLICATE_ITEM_ERROR, EMPTY_ITEM_ERROR, EMPTY_EMAIL_ERROR,
    ExistingListItemForm, ItemForm, NewListForm, ShareListForm
)
from lists.models import Item, List

User = get_user_model()


class ItemFormTest(TestCase):

    def test_form_renders_item_text_input(self):
        form = ItemForm()
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())
        self.assertIn('class="form-control input-lg"', form.as_p())

    def test_form_validation_for_blank_items(self):
        form = ItemForm(data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['text'],
            ["You can't have an empty list item"]
        )


class ExistingListItemFormTest(TestCase):

    def test_form_renders_item_text_input(self):
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_)
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())

    def test_form_validation_for_blank_items(self):
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_, data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['text'],
            [EMPTY_ITEM_ERROR]
        )

    def test_form_validation_for_blank_items(self):
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='no twins!')
        form = ExistingListItemForm(for_list=list_, data={'text': 'no twins!'})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['text'],
            [DUPLICATE_ITEM_ERROR]
        )

    def test_form_save(self):
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_, data={'text': 'hi'})
        new_item = form.save()
        self.assertEqual(new_item, Item.objects.all()[0])


class NewListFormTest(unittest.TestCase):

    @patch('lists.forms.List.create_new')
    def test_creates_new_list_and_item_from_post_data(
        self, mock_List_create_new
    ):
        user = Mock(is_authenticated=False)
        form = NewListForm(data={'text': 'new item text'})
        form.is_valid()
        form.save(owner=user)
        mock_List_create_new.assert_called_once_with(
            first_item_text='new item text'
        )

    @patch('lists.forms.List.create_new')
    def test_creates_new_list_with_owner_if_user_authenticated(
        self, mock_List_create_new
    ):
        user = Mock(is_authenticated=True)
        form = NewListForm(data={'text': 'new item text'})
        form.is_valid()
        form.save(owner=user)
        mock_List_create_new.assert_called_once_with(
            first_item_text='new item text', owner=user
        )

    @patch('lists.forms.List.create_new')
    def test_save_returns_new_list_object(self, mock_List_create_new):
        user = Mock(is_authenticated=True)
        form = NewListForm(data={'text': 'new item text'})
        form.is_valid()
        response = form.save(owner=user)
        self.assertEqual(response, mock_List_create_new.return_value)


class ShareListFormTest(unittest.TestCase):

    def test_form_renders_email_input(self):
        form = ShareListForm()
        self.assertIn('placeholder="your-friend@example.com"', form.as_p())
        self.assertIn('class="form-control"', form.as_p())
        self.assertIn('name="sharee"', form.as_p())

    def test_form_validation_for_blank_email(self):
        form = ShareListForm(data={'shared_with': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['shared_with'],
            [EMPTY_EMAIL_ERROR]
        )

    @patch('lists.forms.List.shared_with')
    def test_shared_email_is_an_existing_user_email(
        self, mock_List_shared_with
    ):
        list_ = List.objects.create()
        user = User.objects.create(email='edith@example.com')
        form = ShareListForm({'shared_with':'edith@example.com', 'id':list_.id})
        form.is_valid()
        form.save()
        mock_List_shared_with.assert_called_once_with(
            is_user_email='edith@example.com'
        )

    @unittest.skip
    def test_shared_email_is__not_an_existing_user_email_user_gets_an_error(self):
        self.fail()
