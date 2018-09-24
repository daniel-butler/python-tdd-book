from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse

class List(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('view_list', args=[self.id])

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
