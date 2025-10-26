from django import forms
from .models import Kid

class KidLoginForm(forms.Form):
    kid = forms.ModelChoiceField(queryset=Kid.objects.filter(active=True))
    pin = forms.CharField(widget=forms.PasswordInput, max_length=20)

class ChangePinForm(forms.Form):
    old_pin = forms.CharField(
        label="Senas PIN",
        widget=forms.PasswordInput(attrs={'placeholder': 'Įvesk seną PIN'}),
        max_length=20
    )
    new_pin = forms.CharField(
        label="Naujas PIN",
        widget=forms.PasswordInput(attrs={'placeholder': 'Įvesk naują PIN'}),
        max_length=20,
        min_length=4,
        help_text="Mažiausiai 4 simboliai"
    )
    confirm_pin = forms.CharField(
        label="Patvirtink naują PIN",
        widget=forms.PasswordInput(attrs={'placeholder': 'Įvesk naują PIN dar kartą'}),
        max_length=20
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_pin = cleaned_data.get('new_pin')
        confirm_pin = cleaned_data.get('confirm_pin')
        
        if new_pin and confirm_pin and new_pin != confirm_pin:
            raise forms.ValidationError("Naujas PIN ir patvirtinimas nesutampa!")
        
        return cleaned_data
