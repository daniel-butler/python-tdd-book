from django.shortcuts import redirect, render

from lists.models import Item


def home_page(request):
    if request.method == 'POST':
        new_item_text = request.POST['item_text']
        Item.objects.create(text=new_item_text)
        return redirect('/lists/the-only-list-in-the-world/')
    return render(request, r'lists\home.html')

def view_list(request):
    items = Item.objects.all()
    return render(request, r'lists\list.html', {'items': items})
