from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from .forms import KidLoginForm
from .models import Kid, Chore, Reward, ChoreLog, Redemption
from django.utils import timezone

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
    # Recent approved history (limit 10 each)
    approved_logs = kid.chore_logs.filter(status=ChoreLog.Status.APPROVED).order_by('-processed_at')[:10]
    approved_redemptions = kid.redemptions.filter(status=Redemption.Status.APPROVED).order_by('-processed_at')[:10]
    # Adventure Map progress data
    map_data = kid.get_map_progress()
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
            "map_data": map_data,
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
