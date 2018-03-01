from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .models import Document
from django import forms
from .forms import ExpForm1, DocumentForm
from django.views.generic.edit import FormView, View
from django.http import JsonResponse
from django.core import validators


@login_required(login_url=reverse_lazy('login'))
def index(request):
    return render(request, 'home.html')

# class ExpFormView(FormView):
#     form_class = ExpForm
#     success_url = "/"
#     template_name = "add_exp.html"
#
#     def form_valid(self, form):
#         exp = form.save(commit=False)
#         exp.user = self.request.user
#         exp.save()
#         return super(ExpFormView, self).form_valid(form)


def add_exp(request):
    if request.method == 'POST':
        if request.is_ajax():
            doc_form = DocumentForm(request.POST, request.FILES)
            if doc_form.is_valid():
                doc = doc_form.save(commit=False)
                doc.user = request.user
                doc.save()
                data = {'is_valid': True, 'id': doc.id, 'name': doc.document.name}
            else:
                data = {'is_valid': False}
            return JsonResponse(data)
        else:
            form = ExpForm1(request.POST)
            context = {'form': form}
            if form.is_valid():
                print('pi')
                exp = form.save(commit=False)
                exp.user = request.user
                exp.save()
                return redirect('home')
    else:
        form = ExpForm1()
        form.fields['doc'] = \
            forms.ModelChoiceField(queryset=request.user.documents.all())
        context = {'form': form, }
    return render(request, 'add_exp.html', context)


def check_exp(request):
    user = request.user
    exp = user.experiments.all()
    return render(request, "check_exp.html", {'exp': exp})


# def add_file(request):
#     if request.method == 'POST' and request.is_ajax():
#         form = DocumentForm(request.POST, request.FILES)
#         if form.is_valid():
#             doc = form.save(commit=False)
#             doc.user = request.user
#             doc.save()
#             data = {'is_valid': True, 'id': doc.id, 'name': doc.document.name}
#         else:
#             data = {'is_valid': False}
#         return JsonResponse(data)
