from django.contrib.auth import get_user_model
from django.forms import EmailInput
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django import forms

from lists.models import Item, List

User = get_user_model()

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

    shared_with = forms.EmailField(
        label=_('Share With'),
        widget=EmailInput(attrs={'placeholder': 'your-friend@example.com', 'class': 'form-control', 'name': 'sharee'}),
        error_messages={'required': EMPTY_EMAIL_ERROR},
    )

    def __init__(self, for_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.list = for_list

    def clean_shared_with(self):
        shared_with = self.cleaned_data['shared_with']
        if len(User.objects.filter(email=shared_with)) != 1:
            shared_with = User.objects.create(email=shared_with)
        else:
            shared_with = User.objects.filter(email=shared_with)[0]
        self.instance.list.shared_with.add(shared_with)
        return shared_with

    class Meta:
        model = List
        exclude = ('shared_with', 'owner')
