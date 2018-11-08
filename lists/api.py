import json

from django.http import HttpResponse

from .models import List, Item
from .forms import ExistingListItemForm, EMPTY_ITEM_ERROR,DUPLICATE_ITEM_ERROR


def list(request, list_id):
    list_ = List.objects.get(id=list_id)
    if request.method == 'POST':
        form = ExistingListItemForm(for_list=list_, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse(status=201)
        else:
            return HttpResponse(
                content=json.dumps({'error': form.errors['text'][0]}),
                status=400,
                content_type='application/json',
            )
    item_dicts = [
        {'id': item.id, 'text': item.text}
        for item in list_.item_set.all()
    ]
    return HttpResponse(
        json.dumps(item_dicts),
        content_type='application/json'
    )
