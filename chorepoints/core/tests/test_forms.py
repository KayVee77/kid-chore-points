"""
Unit tests for core forms.

Tests cover:
- KidLoginForm: validation, kid selection, PIN validation
- ChangePinForm: validation, PIN matching, minimum length
"""

from django.test import TestCase
from django.contrib.auth.models import User
from core.models import Kid
from core.forms import KidLoginForm, ChangePinForm


class KidLoginFormTests(TestCase):
    """Test KidLoginForm validation."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(username='testparent', password='testpass123')
        self.active_kid = Kid.objects.create(
            name='ActiveKid',
            parent=self.user,
            pin='1234',
            active=True
        )
        self.inactive_kid = Kid.objects.create(
            name='InactiveKid',
            parent=self.user,
            pin='5678',
            active=False
        )
    
    def test_form_valid_with_correct_data(self):
        """Test form is valid with correct kid and PIN."""
        form = KidLoginForm(data={
            'kid': self.active_kid.id,
            'pin': '1234'
        })
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_without_kid(self):
        """Test form is invalid without kid selection."""
        form = KidLoginForm(data={
            'pin': '1234'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('kid', form.errors)
    
    def test_form_invalid_without_pin(self):
        """Test form is invalid without PIN."""
        form = KidLoginForm(data={
            'kid': self.active_kid.id
        })
        self.assertFalse(form.is_valid())
        self.assertIn('pin', form.errors)
    
    def test_form_shows_only_active_kids(self):
        """Test form queryset includes only active kids."""
        form = KidLoginForm()
        kid_choices = [kid.id for kid in form.fields['kid'].queryset]
        
        self.assertIn(self.active_kid.id, kid_choices)
        self.assertNotIn(self.inactive_kid.id, kid_choices)
    
    def test_form_invalid_with_nonexistent_kid(self):
        """Test form is invalid with non-existent kid ID."""
        form = KidLoginForm(data={
            'kid': 99999,
            'pin': '1234'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('kid', form.errors)
    
    def test_form_accepts_any_pin_format(self):
        """Test form accepts various PIN formats (validation done in view)."""
        # Form itself doesn't validate PIN correctness, just format
        form = KidLoginForm(data={
            'kid': self.active_kid.id,
            'pin': 'wrong'
        })
        self.assertTrue(form.is_valid())  # Form validation passes, view logic checks correctness
    
    def test_pin_field_is_password_input(self):
        """Test PIN field renders as password input."""
        form = KidLoginForm()
        self.assertEqual(form.fields['pin'].widget.__class__.__name__, 'PasswordInput')
    
    def test_pin_max_length_enforced(self):
        """Test PIN field has max length of 20."""
        form = KidLoginForm()
        self.assertEqual(form.fields['pin'].max_length, 20)


class ChangePinFormTests(TestCase):
    """Test ChangePinForm validation."""
    
    def test_form_valid_with_matching_pins(self):
        """Test form is valid when new PINs match."""
        form = ChangePinForm(data={
            'old_pin': '1234',
            'new_pin': '5678',
            'confirm_pin': '5678'
        })
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_with_mismatched_pins(self):
        """Test form is invalid when new PINs don't match."""
        form = ChangePinForm(data={
            'old_pin': '1234',
            'new_pin': '5678',
            'confirm_pin': '9999'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('nesutampa', form.errors['__all__'][0].lower())
    
    def test_form_invalid_without_old_pin(self):
        """Test form is invalid without old PIN."""
        form = ChangePinForm(data={
            'new_pin': '5678',
            'confirm_pin': '5678'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('old_pin', form.errors)
    
    def test_form_invalid_without_new_pin(self):
        """Test form is invalid without new PIN."""
        form = ChangePinForm(data={
            'old_pin': '1234',
            'confirm_pin': '5678'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('new_pin', form.errors)
    
    def test_form_invalid_without_confirm_pin(self):
        """Test form is invalid without confirm PIN."""
        form = ChangePinForm(data={
            'old_pin': '1234',
            'new_pin': '5678'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('confirm_pin', form.errors)
    
    def test_form_invalid_with_short_pin(self):
        """Test form is invalid with PIN shorter than 4 characters."""
        form = ChangePinForm(data={
            'old_pin': '1234',
            'new_pin': '123',
            'confirm_pin': '123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('new_pin', form.errors)
    
    def test_form_valid_with_minimum_length_pin(self):
        """Test form is valid with 4-character PIN (minimum)."""
        form = ChangePinForm(data={
            'old_pin': '1234',
            'new_pin': '5678',
            'confirm_pin': '5678'
        })
        self.assertTrue(form.is_valid())
    
    def test_form_valid_with_long_pin(self):
        """Test form is valid with PIN up to 20 characters."""
        long_pin = '12345678901234567890'
        form = ChangePinForm(data={
            'old_pin': '1234',
            'new_pin': long_pin,
            'confirm_pin': long_pin
        })
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_with_too_long_pin(self):
        """Test form is invalid with PIN over 20 characters."""
        too_long_pin = '123456789012345678901'  # 21 characters
        form = ChangePinForm(data={
            'old_pin': '1234',
            'new_pin': too_long_pin,
            'confirm_pin': too_long_pin
        })
        self.assertFalse(form.is_valid())
        self.assertIn('new_pin', form.errors)
    
    def test_all_fields_are_password_inputs(self):
        """Test all PIN fields render as password inputs."""
        form = ChangePinForm()
        self.assertEqual(form.fields['old_pin'].widget.__class__.__name__, 'PasswordInput')
        self.assertEqual(form.fields['new_pin'].widget.__class__.__name__, 'PasswordInput')
        self.assertEqual(form.fields['confirm_pin'].widget.__class__.__name__, 'PasswordInput')
    
    def test_field_labels_are_lithuanian(self):
        """Test form field labels are in Lithuanian."""
        form = ChangePinForm()
        self.assertEqual(form.fields['old_pin'].label, 'Senas PIN')
        self.assertEqual(form.fields['new_pin'].label, 'Naujas PIN')
        self.assertEqual(form.fields['confirm_pin'].label, 'Patvirtink naują PIN')
    
    def test_new_pin_has_help_text(self):
        """Test new PIN field has help text about minimum length."""
        form = ChangePinForm()
        self.assertIn('4 simboliai', form.fields['new_pin'].help_text.lower())
    
    def test_form_clean_method_validates_pin_match(self):
        """Test form's clean method properly validates PIN matching."""
        # Valid case
        form = ChangePinForm(data={
            'old_pin': '1234',
            'new_pin': '5678',
            'confirm_pin': '5678'
        })
        self.assertTrue(form.is_valid())
        cleaned_data = form.clean()
        self.assertEqual(cleaned_data['new_pin'], '5678')
        self.assertEqual(cleaned_data['confirm_pin'], '5678')
        
        # Invalid case
        form = ChangePinForm(data={
            'old_pin': '1234',
            'new_pin': '5678',
            'confirm_pin': '9999'
        })
        self.assertFalse(form.is_valid())
    
    def test_form_allows_alphanumeric_pins(self):
        """Test form accepts alphanumeric PINs (not just numbers)."""
        form = ChangePinForm(data={
            'old_pin': 'old1',
            'new_pin': 'new1',
            'confirm_pin': 'new1'
        })
        self.assertTrue(form.is_valid())
    
    def test_form_field_placeholders(self):
        """Test form fields have appropriate placeholders."""
        form = ChangePinForm()
        self.assertIn('Įvesk', form.fields['old_pin'].widget.attrs.get('placeholder', ''))
        self.assertIn('Įvesk', form.fields['new_pin'].widget.attrs.get('placeholder', ''))
        self.assertIn('Įvesk', form.fields['confirm_pin'].widget.attrs.get('placeholder', ''))


class FormIntegrationTests(TestCase):
    """Test form integration scenarios."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(username='testparent', password='testpass123')
        self.kid = Kid.objects.create(
            name='TestKid',
            parent=self.user,
            pin='1234',
            active=True
        )
    
    def test_login_form_with_database_kid(self):
        """Test KidLoginForm works with actual database kid."""
        form = KidLoginForm(data={
            'kid': self.kid.id,
            'pin': '1234'
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['kid'], self.kid)
        self.assertEqual(form.cleaned_data['pin'], '1234')
    
    def test_change_pin_form_full_workflow(self):
        """Test ChangePinForm in complete workflow."""
        # Step 1: Validate form
        form = ChangePinForm(data={
            'old_pin': '1234',
            'new_pin': '5678',
            'confirm_pin': '5678'
        })
        self.assertTrue(form.is_valid())
        
        # Step 2: Would update kid PIN in view (not tested here)
        # This is just form validation
        self.assertEqual(form.cleaned_data['new_pin'], '5678')
    
    def test_multiple_kids_in_login_form(self):
        """Test login form shows multiple active kids."""
        kid2 = Kid.objects.create(
            name='SecondKid',
            parent=self.user,
            pin='9999',
            active=True
        )
        
        form = KidLoginForm()
        kid_ids = [kid.id for kid in form.fields['kid'].queryset]
        
        self.assertEqual(len(kid_ids), 2)
        self.assertIn(self.kid.id, kid_ids)
        self.assertIn(kid2.id, kid_ids)
