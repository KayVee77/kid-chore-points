from django.contrib import admin
from .models import Kid, Chore, Reward, ChoreLog, Redemption, PointAdjustment

@admin.register(Kid)
class KidAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "points_balance", "active", "created_at")
    list_filter = ("active", "parent")
    search_fields = ("name", "parent__username")

@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ("icon_preview", "title", "points", "parent", "active")
    list_filter = ("active", "parent")
    search_fields = ("title",)
    fields = ("parent", "title", "points", "active", "icon_emoji", "icon_image")

    def icon_preview(self, obj):
        if obj.icon_image:
            return f"<img src='{obj.icon_image.url}' style='width:32px; height:32px; object-fit:cover; border-radius:4px;' />"
        if obj.icon_emoji:
            return f"<span style='font-size:1.5rem;'>{obj.icon_emoji}</span>"
        return ""
    icon_preview.short_description = "Ikona"
    icon_preview.allow_tags = True

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ("icon_preview", "title", "cost_points", "parent", "active")
    list_filter = ("active", "parent")
    search_fields = ("title",)
    fields = ("parent", "title", "cost_points", "active", "icon_emoji", "icon_image")

    def icon_preview(self, obj):
        if obj.icon_image:
            return f"<img src='{obj.icon_image.url}' style='width:32px; height:32px; object-fit:cover; border-radius:4px;' />"
        if obj.icon_emoji:
            return f"<span style='font-size:1.5rem;'>{obj.icon_emoji}</span>"
        return ""
    icon_preview.short_description = "Ikona"
    icon_preview.allow_tags = True

@admin.register(ChoreLog)
class ChoreLogAdmin(admin.ModelAdmin):
    list_display = ("child", "chore", "points_awarded", "status", "logged_at", "processed_at")
    list_filter = ("child", "chore", "status")
    actions = ["approve_selected", "reject_selected"]

    def approve_selected(self, request, queryset):
        count = 0
        for log in queryset:
            if log.approve():
                count += 1
        self.message_user(request, f"Patvirtinta {count} darbų įrašų.")
    approve_selected.short_description = "Patvirtinti pasirinktus laukiančius darbus"

    def reject_selected(self, request, queryset):
        count = 0
        for log in queryset:
            if log.reject():
                count += 1
        self.message_user(request, f"Atmesta {count} darbų įrašų.")
    reject_selected.short_description = "Atmesti pasirinktus laukiančius darbus"

@admin.register(Redemption)
class RedemptionAdmin(admin.ModelAdmin):
    list_display = ("child", "reward", "cost_points", "status", "redeemed_at", "processed_at")
    list_filter = ("child", "reward", "status")
    actions = ["approve_selected", "reject_selected"]

    def approve_selected(self, request, queryset):
        count = 0
        for red in queryset:
            if red.approve():
                count += 1
        self.message_user(request, f"Patvirtinta {count} apdovanojimų.")
    approve_selected.short_description = "Patvirtinti pasirinktus laukiančius apdovanojimus"

    def reject_selected(self, request, queryset):
        count = 0
        for red in queryset:
            if red.reject():
                count += 1
        self.message_user(request, f"Atmesta {count} apdovanojimų.")
    reject_selected.short_description = "Atmesti pasirinktus laukiančius apdovanojimus"

@admin.register(PointAdjustment)
class PointAdjustmentAdmin(admin.ModelAdmin):
    list_display = ("kid", "parent", "points", "reason", "created_at")
    list_filter = ("parent", "kid")
    search_fields = ("kid__name", "reason")
