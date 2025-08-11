from django.db import migrations, models
import django.utils.timezone

def approve_existing(apps, schema_editor):
    ChoreLog = apps.get_model('core', 'ChoreLog')
    Redemption = apps.get_model('core', 'Redemption')
    now = django.utils.timezone.now()
    for log in ChoreLog.objects.all():
        # legacy logs already applied points; mark approved
        log.status = 'APPROVED'
        log.processed_at = now
        log.save(update_fields=['status', 'processed_at'])
    for red in Redemption.objects.all():
        # legacy redemptions already deducted points; mark approved
        red.status = 'APPROVED'
        red.processed_at = now
        red.save(update_fields=['status', 'processed_at'])

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chorelog',
            name='processed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='chorelog',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING', max_length=10),
        ),
        migrations.AddField(
            model_name='redemption',
            name='processed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='redemption',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING', max_length=10),
        ),
        migrations.RunPython(approve_existing, reverse_code=migrations.RunPython.noop),
    ]
