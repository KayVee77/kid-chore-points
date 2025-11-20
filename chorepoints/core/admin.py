from django.contrib import admin
from django.utils.html import mark_safe
from .models import Kid, Chore, Reward, ChoreLog, Redemption, PointAdjustment
from .admin_forms import ChoreAdminForm, RewardAdminForm

# Customize default admin site
admin.site.site_title = "Taškų sistema"
admin.site.site_header = "Taškų sistema - Tėvų skydelis"
admin.site.index_title = "Valdymo skydelis"

@admin.register(Kid)
class KidAdmin(admin.ModelAdmin):
    list_display = ("name", "gender", "parent", "points_balance", "map_position", "map_theme", "active", "created_at")
    list_filter = ("active", "parent", "map_theme", "gender")
    search_fields = ("name", "parent__username")
    actions = ["reset_map_position"]
    fieldsets = (
        ("Pagrindinė informacija", {
            'fields': ('parent', 'name', 'gender', 'pin', 'active')
        }),
        ("Taškai ir žemėlapis", {
            'fields': ('points_balance', 'map_position', 'highest_milestone', 'map_theme')
        }),
        ("Avataro nustatymai", {
            'fields': ('avatar_emoji', 'photo')
        }),
    )
    
    def reset_map_position(self, request, queryset):
        count = queryset.update(map_position=0)
        self.message_user(request, f"Atstatyta {count} vaikų žemėlapio pozicija į 0.")
    reset_map_position.short_description = "Atstatyti žemėlapio poziciją (0)"

@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    form = ChoreAdminForm
    list_display = ("icon_preview", "title", "points", "parent", "active")
    list_filter = ("active", "parent")
    search_fields = ("title",)
    fields = ("parent", "title", "points", "active", "icon_emoji", "icon_image")

    def icon_preview(self, obj):
        if obj.icon_image:
            return mark_safe(f"<img src='{obj.icon_image.url}' style='width:32px; height:32px; object-fit:cover; border-radius:4px;' />")
        if obj.icon_emoji:
            return mark_safe(f"<span style='font-size:1.5rem;'>{obj.icon_emoji}</span>")
        return ""
    icon_preview.short_description = "Ikona"

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    form = RewardAdminForm
    list_display = ("icon_preview", "title", "cost_points", "parent", "active")
    list_filter = ("active", "parent")
    search_fields = ("title",)
    fields = ("parent", "title", "cost_points", "active", "icon_emoji", "icon_image")

    def icon_preview(self, obj):
        if obj.icon_image:
            return mark_safe(f"<img src='{obj.icon_image.url}' style='width:32px; height:32px; object-fit:cover; border-radius:4px;' />")
        if obj.icon_emoji:
            return mark_safe(f"<span style='font-size:1.5rem;'>{obj.icon_emoji}</span>")
        return ""
    icon_preview.short_description = "Ikona"

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
    list_display = ("created_at", "kid", "points_display", "reason", "parent")
    list_filter = ("parent", "kid", "created_at")
    search_fields = ("kid__name", "reason")
    fields = ("kid", "points", "reason")
    readonly_fields = ("parent", "created_at")
    ordering = ("-created_at",)
    
    def points_display(self, obj):
        color = "green" if obj.points > 0 else "red"
        sign = "+" if obj.points >= 0 else ""
        return mark_safe(f"<span style='color:{color}; font-weight:bold;'>{sign}{obj.points}</span>")
    points_display.short_description = "Taškai"
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set parent on creation
            obj.parent = request.user
        super().save_model(request, obj, form, change)
