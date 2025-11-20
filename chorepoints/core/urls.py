from django.urls import path
from . import views

urlpatterns = [
    path('health-check/', views.health_check, name='health_check'),
    path('login/', views.kid_login, name='kid_login'),
    path('logout/', views.kid_logout, name='kid_logout'),
    path('home/', views.kid_home, name='kid_home'),
    path('change-pin/', views.change_pin, name='change_pin'),
    path('upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('chore/<int:chore_id>/complete/', views.complete_chore, name='complete_chore'),
    path('reward/<int:reward_id>/redeem/', views.redeem_reward, name='redeem_reward'),
]
