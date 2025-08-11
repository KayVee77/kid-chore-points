from django import forms
from .models import Kid

class KidLoginForm(forms.Form):
    kid = forms.ModelChoiceField(queryset=Kid.objects.filter(active=True))
    pin = forms.CharField(widget=forms.PasswordInput, max_length=20)
