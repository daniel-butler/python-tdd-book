from django.forms import EmailInput
from django.core.exceptions import ValidationError
from django import forms

from lists.models import Item, List

EMPTY_ITEM_ERROR = "You can't have an empty list item"
DUPLICATE_ITEM_ERROR = "You've already got this in your list"
EMPTY_EMAIL_ERROR = "Email not filled in"


class ItemForm(forms.models.ModelForm):

    class Meta:
        model = Item
        fields = ('text',)
        widgets = {
            'text': forms.fields.TextInput(attrs={
                'placeholder': 'Enter a to-do item',
                'class': 'form-control input-lg',
            }),
        }
        error_messages = {
            'text': {'required': EMPTY_ITEM_ERROR},
        }


class NewListForm(ItemForm):

    def save(self, owner):
        if owner.is_authenticated:
            return List.create_new(
                first_item_text=self.cleaned_data['text'], owner=owner
            )
        else:
            return List.create_new(first_item_text=self.cleaned_data['text'])


class ExistingListItemForm(ItemForm):
    def __init__(self, for_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.list = for_list

    def validate_unique(self):
        try:
            self.instance.validate_unique()
        except ValidationError as e:
            e.error_dict = {'text': [DUPLICATE_ITEM_ERROR]}
            self._update_errors(e)


class ShareListForm(forms.models.ModelForm):

    class Meta:
        model = List
        fields = ('shared_with',)
        widgets = {
            'shared_with': EmailInput(attrs={
                'placeholder': 'your-friend@example.com',
                'class': 'form-control',
                'name': 'sharee',
            },
                label='Share With'
            ),
        }
        error_messages = {
            'shared_with': {'required': EMPTY_EMAIL_ERROR}
        }
