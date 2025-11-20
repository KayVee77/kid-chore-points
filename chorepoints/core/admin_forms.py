from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from core.models import Chore, Reward

# Curated set of common emojis for chores/rewards so admins can pick quickly (emoji-only display).
EMOJI_SUGGESTIONS = [
    "🧹", "🧽", "🗑️", "🧺", "🧼", "🧦", "🛏️", "🧸", "🧻", "🧴",
    "🍽️", "🍲", "🍎", "🥕", "🥪", "🧁", "🍕", "🍜", "🍇", "🥛",
    "📚", "✏️", "🖍️", "🖥️", "🎧", "🎮", "🎲", "🧩", "🎼", "📺",
    "🏀", "⚽", "🚲", "🛴", "🏃", "🧘", "🧗", "🏊", "⛹️", "🏸",
    "🌿", "🌻", "🌳", "🪴", "🐶", "🐱", "🐟", "🐢", "💧", "🔥",
]


class EmojiDatalistTextInput(forms.TextInput):
    """Text input with an attached datalist of emoji suggestions."""

    def __init__(self, emoji_choices=None, *args, **kwargs):
        self.emoji_choices = emoji_choices or []
        attrs = kwargs.setdefault("attrs", {})
        attrs.setdefault("placeholder", "Emoji")
        attrs.setdefault("style", "width: 4ch; font-size: 1.5rem; text-align: center; padding: 4px;")
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        datalist_id = attrs.get("list") or f"{attrs.get('id', name)}-emoji-options"
        attrs["list"] = datalist_id
        input_id = attrs.get("id", name)
        input_html = super().render(name, value, attrs, renderer)

        options_html = "".join(
            format_html('<option value="{}"></option>', emoji) for emoji in self.emoji_choices
        )
        datalist_html = format_html('<datalist id="{}">{}</datalist>', datalist_id, mark_safe(options_html))

        grid_buttons = "".join(
            format_html(
                "<button type='button' class='emoji-choice' data-emoji='{0}' aria-label='{0}'>{0}</button>",
                emoji
            )
            for emoji in self.emoji_choices
        )
        grid_html = format_html(
            "<div class='emoji-grid' data-input-id='{0}'>{1}</div>",
            input_id,
            mark_safe(grid_buttons),
        )

        style_and_script = format_html(
            """
<style>
.emoji-grid {{
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 12px;
  max-width: 380px;
  padding: 8px;
  background: rgba(0,0,0,0.02);
  border-radius: 8px;
  border: 1px solid rgba(0,0,0,0.08);
}}
.emoji-choice {{
  border: 1px solid rgba(0,0,0,0.08);
  background: white;
  color: inherit;
  width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  font-size: 1.3rem;
  cursor: pointer;
  transition: all 100ms ease;
}}
.emoji-choice:hover {{
  border-color: rgba(0,0,0,0.2);
  background: rgba(96,165,250,0.1);
  transform: scale(1.08);
  outline: none;
}}
.emoji-choice:focus {{
  border-color: #60a5fa;
  outline: none;
  box-shadow: 0 0 0 2px rgba(96,165,250,0.2);
}}
.emoji-choice.active {{
  border-color: #60a5fa;
  background: rgba(96,165,250,0.15);
  box-shadow: 0 0 0 2px rgba(96,165,250,0.3);
}}
</style>
<script>
(function() {{
  if (window.__emojiPickerBound__) {{ return; }}
  window.__emojiPickerBound__ = true;
  document.addEventListener('click', function(evt) {{
    var btn = evt.target.closest('.emoji-choice');
    if (!btn) return;
    var grid = btn.closest('.emoji-grid');
    if (!grid) return;
    var inputId = grid.getAttribute('data-input-id');
    var input = document.getElementById(inputId);
    if (!input) return;
    input.value = btn.getAttribute('data-emoji');
    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
    grid.querySelectorAll('.emoji-choice.active').forEach(function(el) {{
      el.classList.remove('active');
    }});
    btn.classList.add('active');
  }}, true);
}})();
</script>
"""
        )

        return mark_safe(f"{input_html}{datalist_html}{grid_html}{style_and_script}")


class ChoreAdminForm(forms.ModelForm):
    """Admin form for Chore with emoji suggestions."""

    icon_emoji = forms.CharField(
        required=False,
        max_length=8,
        label="Emoji ikona",
        help_text=Chore._meta.get_field("icon_emoji").help_text,
        widget=EmojiDatalistTextInput(emoji_choices=EMOJI_SUGGESTIONS),
    )

    class Meta:
        model = Chore
        fields = ("parent", "title", "points", "active", "icon_emoji", "icon_image")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_help = Chore._meta.get_field("icon_emoji").help_text or ""
        self.fields["icon_emoji"].help_text = (
            f"{base_help} Pasirink emoji paspaudimu arba įvesk savo simbolį."
        )


from core.models import Reward

class RewardAdminForm(forms.ModelForm):
    """Admin form for Reward with emoji suggestions."""

    icon_emoji = forms.CharField(
        required=False,
        max_length=8,
        label="Emoji ikona",
        help_text=Reward._meta.get_field("icon_emoji").help_text,
        widget=EmojiDatalistTextInput(emoji_choices=EMOJI_SUGGESTIONS),
    )

    class Meta:
        model = Reward
        fields = ("parent", "title", "cost_points", "active", "icon_emoji", "icon_image")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_help = Reward._meta.get_field("icon_emoji").help_text or ""
        self.fields["icon_emoji"].help_text = (
            f"{base_help} Pasirink emoji paspaudimu arba įvesk savo simbolį."
        )
