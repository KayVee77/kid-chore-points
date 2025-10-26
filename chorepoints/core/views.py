from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from .forms import KidLoginForm, ChangePinForm
from .models import Kid, Chore, Reward, ChoreLog, Redemption
from django.utils import timezone
import json

def index(request):
    return render(request, "index.html")

@require_http_methods(["GET", "POST"])
def kid_login(request):
    form = KidLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        kid = form.cleaned_data["kid"]
        pin = form.cleaned_data["pin"]
        if kid.active and kid.pin == pin:
            request.session["kid_id"] = kid.id
            messages.success(request, f"Sveikas, {kid.name}!")
            return redirect("kid_home")
        messages.error(request, "Neteisingas PIN arba paskyra neaktyvi.")
    return render(request, "kid/login.html", {"form": form})

def kid_logout(request):
    request.session.pop("kid_id", None)
    messages.info(request, "Atsijungta.")
    return redirect("index")

def _get_kid(request):
    kid_id = request.session.get("kid_id")
    if not kid_id:
        return None
    return get_object_or_404(Kid, pk=kid_id, active=True)

def kid_home(request):
    kid = _get_kid(request)
    if not kid:
        return redirect("kid_login")
    chores = Chore.objects.filter(parent=kid.parent, active=True).order_by("title")
    rewards = Reward.objects.filter(parent=kid.parent, active=True).order_by("cost_points")
    pending_logs = kid.chore_logs.filter(status=ChoreLog.Status.PENDING).order_by('-logged_at')
    pending_redemptions = kid.redemptions.filter(status=Redemption.Status.PENDING).order_by('-redeemed_at')
    pending_chore_ids = list(pending_logs.values_list('chore_id', flat=True))
    pending_reward_ids = list(pending_redemptions.values_list('reward_id', flat=True))

    # Progress to next reward
    next_reward = None
    progress_percent = 0
    if rewards:
        # reward just above current balance
        higher = [r for r in rewards if r.cost_points > kid.points_balance]
        if higher:
            next_reward = higher[0]
            progress_percent = int(min(100, (kid.points_balance / next_reward.cost_points) * 100))
        else:
            # already can afford all rewards
            next_reward = rewards.last()  # most expensive
            progress_percent = 100

    # Confetti trigger: detect newly approved logs or redemptions since last visit
    last_seen_iso = request.session.get("last_seen_approval_ts")
    approved_new = False
    now_ts = timezone.now()
    if last_seen_iso:
        try:
            last_seen_dt = timezone.datetime.fromisoformat(last_seen_iso)
            if timezone.is_naive(last_seen_dt):
                last_seen_dt = timezone.make_aware(last_seen_dt, timezone.get_current_timezone())
        except Exception:
            last_seen_dt = None
        if last_seen_dt:
            new_approved_logs = kid.chore_logs.filter(status=ChoreLog.Status.APPROVED, processed_at__gt=last_seen_dt).exists()
            new_approved_reds = kid.redemptions.filter(status=Redemption.Status.APPROVED, processed_at__gt=last_seen_dt).exists()
            approved_new = new_approved_logs or new_approved_reds
    # update timestamp AFTER computing
    request.session["last_seen_approval_ts"] = now_ts.isoformat()
    
    # Milestone unlock detection: check if map_position has advanced
    last_seen_map_position = request.session.get("last_seen_map_position", 0)
    milestone_unlocked = kid.map_position > last_seen_map_position
    newly_unlocked_milestones = []
    old_map_position = last_seen_map_position  # Store for animation
    if milestone_unlocked:
        # Find which milestones were just unlocked
        map_data_temp = kid.get_map_progress()
        for milestone in map_data_temp['milestones']:
            if last_seen_map_position < milestone['position'] <= kid.map_position:
                newly_unlocked_milestones.append(milestone)
    # Update last seen map position
    request.session["last_seen_map_position"] = kid.map_position
    
    # Track newly affordable rewards (treasure unlock effect)
    last_seen_balance = request.session.get("last_seen_balance", kid.points_balance)
    points_changed = kid.points_balance != last_seen_balance
    old_points_balance = last_seen_balance
    newly_affordable_reward_ids = []
    if kid.points_balance > last_seen_balance:
        # Find rewards that just became affordable
        for reward in rewards:
            if last_seen_balance < reward.cost_points <= kid.points_balance:
                newly_affordable_reward_ids.append(reward.id)
    # Update last seen balance AFTER we've captured the old value
    request.session["last_seen_balance"] = kid.points_balance
    
    # Recent approved history (limit 10 each)
    approved_logs = kid.chore_logs.filter(status=ChoreLog.Status.APPROVED).order_by('-processed_at')[:10]
    approved_redemptions = kid.redemptions.filter(status=Redemption.Status.APPROVED).order_by('-processed_at')[:10]
    
    # Get recent point adjustments (both positive and negative)
    recent_adjustments = kid.point_adjustments.order_by('-created_at')[:10]
    
    # Adventure Map progress data
    map_data = kid.get_map_progress()
    
    # Calculate old progress percentage for movement animation
    old_progress_percentage = 0
    if milestone_unlocked and map_data['milestones']:
        # Calculate where the kid was before
        next_milestone_pos = None
        prev_milestone_pos = 0
        for milestone in map_data['milestones']:
            if milestone['position'] > old_map_position:
                next_milestone_pos = milestone['position']
                break
            prev_milestone_pos = milestone['position']
        
        if next_milestone_pos:
            segment_length = next_milestone_pos - prev_milestone_pos
            progress_in_segment = old_map_position - prev_milestone_pos
            if segment_length > 0:
                old_progress_percentage = min(100, int((progress_in_segment / segment_length) * 100))
    
    # Convert Django messages to JSON for toast notifications
    django_messages = []
    storage = messages.get_messages(request)
    for message in storage:
        level_map = {
            messages.SUCCESS: 'success',
            messages.INFO: 'info',
            messages.WARNING: 'info',
            messages.ERROR: 'error',
        }
        django_messages.append({
            'message': str(message),
            'level': level_map.get(message.level, 'info')
        })
    
    return render(
        request,
        "kid/home.html",
        {
            "kid": kid,
            "chores": chores,
            "rewards": rewards,
            "pending_logs": pending_logs,
            "pending_redemptions": pending_redemptions,
            "next_reward": next_reward,
            "progress_percent": progress_percent,
            "approved_new": approved_new,
            "pending_chore_ids": pending_chore_ids,
            "pending_reward_ids": pending_reward_ids,
            "approved_logs": approved_logs,
            "approved_redemptions": approved_redemptions,
            "recent_adjustments": recent_adjustments,
            "map_data": map_data,
            "milestone_unlocked": milestone_unlocked,
            "newly_unlocked_milestones": newly_unlocked_milestones,
            "newly_unlocked_milestones_json": json.dumps(newly_unlocked_milestones),
            "old_map_position": old_map_position,
            "old_progress_percentage": old_progress_percentage,
            "newly_affordable_reward_ids": newly_affordable_reward_ids,
            "django_messages_json": json.dumps(django_messages),
            "points_changed": points_changed,
            "old_points_balance": old_points_balance,
        },
    )

@require_http_methods(["POST"])
def complete_chore(request, chore_id):
    kid = _get_kid(request)
    if not kid:
        return redirect("kid_login")
    chore = get_object_or_404(Chore, pk=chore_id, parent=kid.parent, active=True)
    # Prevent duplicate pending submission for same chore
    if ChoreLog.objects.filter(child=kid, chore=chore, status=ChoreLog.Status.PENDING).exists():
        messages.info(request, "Šis darbas jau laukia patvirtinimo.")
        return redirect("kid_home")
    ChoreLog.objects.create(child=kid, chore=chore, points_awarded=chore.points)
    messages.success(request, f"Pateikta patvirtinimui: '{chore.title}' (+{chore.points} tšk). Laukia tėvų patvirtinimo.")
    return redirect("kid_home")

@require_http_methods(["POST"])
def redeem_reward(request, reward_id):
    kid = _get_kid(request)
    if not kid:
        return redirect("kid_login")
    reward = get_object_or_404(Reward, pk=reward_id, parent=kid.parent, active=True)
    # Prevent duplicate pending request for same reward
    if Redemption.objects.filter(child=kid, reward=reward, status=Redemption.Status.PENDING).exists():
        messages.info(request, "Šis apdovanojimo prašymas jau laukia patvirtinimo.")
        return redirect("kid_home")
    # create pending request (points will be deducted upon approval)
    Redemption.objects.create(child=kid, reward=reward, cost_points=reward.cost_points)
    messages.success(request, f"Prašymas dėl apdovanojimo: '{reward.title}' ({reward.cost_points} tšk) pateiktas ir laukia patvirtinimo.")
    return redirect("kid_home")

@require_http_methods(["GET", "POST"])
def change_pin(request):
    """Allow kid to change their own PIN by verifying the old one first."""
    kid = _get_kid(request)
    if not kid:
        return redirect("kid_login")
    
    if request.method == "POST":
        form = ChangePinForm(request.POST)
        if form.is_valid():
            old_pin = form.cleaned_data['old_pin']
            new_pin = form.cleaned_data['new_pin']
            
            # Verify old PIN
            if kid.pin != old_pin:
                messages.error(request, "Neteisingas senas PIN. Bandyk dar kartą.")
                return render(request, "kid/change_pin.html", {"form": form, "kid": kid})
            
            # Update to new PIN
            kid.pin = new_pin
            kid.save()
            messages.success(request, "PIN sėkmingai pakeistas! Dabar gali naudoti naują PIN prisijungimui.")
            return redirect("kid_home")
    else:
        form = ChangePinForm()
    
    return render(request, "kid/change_pin.html", {"form": form, "kid": kid})
