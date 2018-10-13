from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse


class List(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='list_shared_with',
        related_query_name='list_shared_withs'
,    )

    def get_absolute_url(self):
        return reverse('view_list', args=[self.id])

    @staticmethod
    def create_new(first_item_text, owner=None):
        list_ = List.objects.create(owner=owner)
        Item.objects.create(text=first_item_text, list=list_)
        return list_

    @property
    def name(self):
        return self.item_set.first().text


class Item(models.Model):
    text = models.TextField(default='', blank=False)
    list = models.ForeignKey(List, default=None)

    class Meta:
        unique_together = (('list', 'text'),)
        ordering = ['id',]

    def __str__(self):
        return self.text
