from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import Chore, Reward
from core.admin_forms import ChoreAdminForm, RewardAdminForm

User = get_user_model()

class AdminEmojiPickerTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_chore_add_view_uses_custom_form(self):
        url = reverse('admin:core_chore_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check if the response contains the emoji grid HTML
        self.assertContains(response, "emoji-grid")
        self.assertContains(response, 'data-emoji=')
        self.assertContains(response, 'Emoji ikona')

    def test_reward_add_view_uses_custom_form(self):
        url = reverse('admin:core_reward_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check if the response contains the emoji grid HTML
        self.assertContains(response, "emoji-grid")
        self.assertContains(response, 'data-emoji=')

    def test_chore_change_view_uses_custom_form(self):
        chore = Chore.objects.create(parent=self.admin_user, title="Test Chore", points=5)
        url = reverse('admin:core_chore_change', args=[chore.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "emoji-grid")

