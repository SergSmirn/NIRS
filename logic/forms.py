from django import forms
from .models import Experiment, Particle


class ExpForm(forms.ModelForm):

    particle = forms.ModelChoiceField(queryset=Particle.objects.all(), empty_label="Particle")

    class Meta:
        model = Experiment
        fields = {'particle', 'energy'}
