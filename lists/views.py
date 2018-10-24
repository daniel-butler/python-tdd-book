from django.views.generic import FormView, CreateView, DetailView
from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model

from lists.models import Item, List
from lists.forms import ItemForm, ExistingListItemForm, NewListForm, ShareListForm

User = get_user_model()


class HomePageView(FormView):
    template_name = 'lists/home.html'
    form_class = ItemForm


class ViewAndAddToList(DetailView, CreateView):
    model = List
    template_name = 'lists/list.html'
    form_class = ExistingListItemForm
    share_form = ShareListForm

    def get_form(self):
        self.object = self.get_object()
        return self.form_class(for_list=self.object, data=self.request.POST)

    def get(self, request, pk, *args, **kwargs):
        list_ = List.objects.get(id=pk)
        form = ExistingListItemForm(for_list=list_)
        share_form = ShareListForm()
        return render(
            request, r'lists/list.html',
            {'list': list_, 'form': form, 'share_form': share_form}
        )


def my_lists(request, email):
    owner = User.objects.get(email=email)
    return render(request, 'lists/my_lists.html', {'owner': owner})


class NewListView(CreateView):
    form_class = NewListForm
    template_name = 'lists/home.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            list_ = form.save(owner=request.user)
            return redirect(list_)
        return render(request, 'lists/home.html', {'form': form})


def share(request, list_id):
    list_ = List.objects.get(id=list_id)
    if request.method == 'POST':
        email = request.POST['sharee']
        if len(User.objects.filter(email=email)) == 0:
            user = User.objects.create(email=email)
            user.save()
        list_.shared_with.add(email)
    return redirect(list_)
