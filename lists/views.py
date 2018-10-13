from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from lists.models import Item, List
from lists.forms import ItemForm, ExistingListItemForm, NewListForm

User = get_user_model()


def home_page(request):
    return render(request, r'lists/home.html', {'form': ItemForm()})

def view_list(request, list_id):
    list_ = List.objects.get(id=list_id)
    form = ExistingListItemForm(for_list=list_)
    if request.method == 'POST':
        form = ExistingListItemForm(for_list=list_, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(list_)
    return render(request, r'lists/list.html', {'list': list_, 'form': form,})

def my_lists(request, email):
    owner = User.objects.get(email=email)
    return render(request, 'lists/my_lists.html', {'owner': owner})

def new_list(request):
    form = NewListForm(data=request.POST)
    if form.is_valid():
        list_ = form.save(owner=request.user)
        return redirect(list_)
    return render(request, 'lists/home.html', {'form': form})

def share(request, list_id):
    list_ = List.objects.get(id=list_id)
    if request.method == 'POST':
        email = request.POST['email']
        list_.shared_with.add(email)
    return redirect(list_)
