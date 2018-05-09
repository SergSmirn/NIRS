from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .forms import ExperimentForm, DeviceForm
from .models import Device
from django.http import JsonResponse
import numpy as np
import pandas as pd
from logic.task import run_calc


@login_required(login_url=reverse_lazy('login'))
def index(request):
    return render(request, 'home.html')


def add_exp(request):
    if request.method == 'POST':
        if 'name' in request.POST:
            device_form = DeviceForm(request.POST)
            form = ExperimentForm(request.user, request.POST, request.FILES)

            if device_form.is_valid() and form.is_valid():
                device_form.save(commit=False)

                device = Device(user=request.user)
                device.name = request.POST['name']
                device.process_node = request.POST['process_node']
                device.supply_voltage = request.POST['supply_voltage']
                device.resistance = request.POST['resistance']
                device.capacitance = request.POST['capacitance']
                device.save()

                exp = form.save(commit=False)
                exp.device = device
                exp.user = request.user
                exp_data = request.FILES['data']
                df = pd.read_excel(exp_data, sheet_name='Sheet1')
                device.experimental_data = [list(df.as_matrix().T[0]), list(df.as_matrix().T[1])]
                let = request.FILES['let']
                exp.spectre = np.loadtxt(let, skiprows=23).tolist()

                device.save()
                exp.save()

                run_calc.delay(exp.pk)

                return redirect('home')

        if 'device' in request.POST:
            if request.POST.get('device') == '':
                form = ExperimentForm(request.user, request.POST, request.FILES)
                device_form = DeviceForm()
                return render(request, 'add_file.html', {'form': form, 'device_form': device_form, 'status': 'fail'})

        form = ExperimentForm(request.user, request.POST, request.FILES)

        if form.is_valid():
            exp = form.save(commit=False)
            device = Device.objects.get(pk=request.POST.get('device'))
            exp.user = request.user
            exp.device = device
            exp_data = request.FILES['data']
            df = pd.read_excel(exp_data, sheet_name='Sheet1')
            device.experimental_data = [list(df.as_matrix().T[0]), list(df.as_matrix().T[1])]
            let = request.FILES['let']
            exp.spectre = np.loadtxt(let, skiprows=23).tolist()
            device.save()
            exp.save()
            run_calc.delay(exp.pk)

            return redirect('home')
        device_form = DeviceForm(request.POST)
        return render(request, 'add_file.html', {'form': form, 'device_form': device_form})
    else:
        form = ExperimentForm(request.user)
        device_form = DeviceForm()
    return render(request, 'add_file.html', {'form': form, 'device_form': device_form})


# def get_devices(request):
#     if request.method == 'GET' and request.is_ajax():
#         ads
#     return 0
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


# def add_exp(request):
#     if request.method == 'POST':
#         if request.is_ajax():
#             doc_form = DocumentForm(request.POST, request.FILES)
#             if doc_form.is_valid():
#                 doc = doc_form.save(commit=False)
#                 doc.user = request.user
#                 doc.save()
#                 data = {'is_valid': True, 'id': doc.id, 'name': doc.document.name}
#             else:
#                 data = {'is_valid': False}
#             return JsonResponse(data)
#         else:
#             form = ExpForm1(request.POST)
#             context = {'form': form}
#             if form.is_valid():
#                 print('pi')
#                 exp = form.save(commit=False)
#                 exp.user = request.user
#                 exp.save()
#                 return redirect('home')
#     else:
#         form = ExpForm1()
#         form.fields['doc'] = \
#             forms.ModelChoiceField(queryset=request.user.documents.all())
#         context = {'form': form, }
#     return render(request, 'add_exp.html', context)
#
#
# def check_exp(request):
#     user = request.user
#     exp = user.experiments.all()
#     return render(request, "check_exp.html", {'exp': exp})


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
