from django import forms
from .models import Experiment, Document


class ExpForm1(forms.ModelForm):

    class Meta:
        model = Experiment
        fields = ('doc','param')


class ExpForm2(forms.ModelForm):

    class Meta:
        model = Experiment
        fields = ('param',)


class DocumentForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = ('document',)
