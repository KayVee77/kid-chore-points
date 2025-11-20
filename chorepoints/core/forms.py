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

class AvatarUploadForm(forms.ModelForm):
    """Form for uploading kid avatar photo or selecting emoji."""
    class Meta:
        model = Kid
        fields = ['photo', 'avatar_emoji']
        widgets = {
            'avatar_emoji': forms.TextInput(attrs={
                'placeholder': '😀',
                'maxlength': '4',
                'class': 'emoji-input'
            })
        }
        labels = {
            'photo': 'Įkelti nuotrauką',
            'avatar_emoji': 'Arba pasirink emoji'
        }
        help_texts = {
            'photo': 'Maksimalus dydis: 5MB. Palaikomi formatai: JPG, PNG, GIF',
            'avatar_emoji': 'Įvesk emoji simbolį (pvz., 😀 🎮 🚀)'
        }
    
    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            # Validate file size (max 5MB)
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Nuotrauka per didelė! Maksimalus dydis: 5MB")
            
            # Validate file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if hasattr(photo, 'content_type') and photo.content_type not in allowed_types:
                raise forms.ValidationError("Netinkamas failas! Leistini formatai: JPG, PNG, GIF")
        
        return photo
    
    def clean(self):
        cleaned_data = super().clean()
        photo = cleaned_data.get('photo')
        avatar_emoji = cleaned_data.get('avatar_emoji')
        
        # At least one must be provided (or both can be cleared to reset)
        # This allows flexibility - kids can switch between photo and emoji
        
        return cleaned_data
