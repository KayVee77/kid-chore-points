from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0003_kid_avatar_emoji'),
    ]

    operations = [
        migrations.CreateModel(
            name='PointAdjustment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField(help_text='Positive or negative integer to adjust balance')),
                ('reason', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('kid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='point_adjustments', to='core.kid')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='point_adjustments', to='auth.user')),
            ],
        ),
    ]
