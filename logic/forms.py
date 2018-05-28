from django import forms
from .models import Experiment, Device


class ExperimentForm(forms.ModelForm):
    data = forms.FileField(label='Результаты эксперемента')
    let = forms.FileField(label='Спектр')
    device = forms.ModelChoiceField(queryset=Device.objects.none(), required=False)

    def __init__(self, user, *args, **kwargs):
        super(ExperimentForm, self).__init__(*args, **kwargs)
        self.fields['device'].queryset = Device.objects.filter(user=user.id)

    class Meta:
        model = Experiment
        exclude = ('user', 'simulation_result', 'par1', 'par2', 'spectre', 'experimental_data', 'ser')


class DeviceForm(forms.ModelForm):

    class Meta:
        model = Device
        exclude = ('user',)
