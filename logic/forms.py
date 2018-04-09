from django import forms
from .models import Experiment


class ExperimentForm(forms.ModelForm):
    data = forms.FileField(label='Результаты эксперемента')
    let = forms.FileField(label='Спектр')

    class Meta:
        model = Experiment
        exclude = ('experimental_data', 'user', 'simulation_result', 'par1', 'par2', 'spectre')
