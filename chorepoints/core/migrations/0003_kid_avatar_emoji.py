from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_chorelog_redemption_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='kid',
            name='avatar_emoji',
            field=models.CharField(default='😀', help_text='Short emoji to show as avatar', max_length=4),
        ),
    ]
