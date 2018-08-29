from django.http import HttpResponse
from django.shortcuts import render


def home_page(request):
    return render(request, r'lists\home.html', {
        'new_item_text': request.POST.get('item_text', ''),
    })
