# Generated data migration to add initial chores and rewards from CSV files

from django.db import migrations
import csv
import os

def add_initial_data(apps, schema_editor):
    """Add initial Lithuanian chores and rewards from CSV files."""
    User = apps.get_model('auth', 'User')
    Chore = apps.get_model('core', 'Chore')
    Reward = apps.get_model('core', 'Reward')
    
    # Get the first superuser (parent account)
    parent = User.objects.filter(is_superuser=True).first()
    if not parent:
        print("No superuser found - skipping initial data creation")
        return
    
    # Get the path to CSV files
    migration_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(os.path.dirname(migration_dir))
    csv_dir = os.path.join(project_root, 'initial_data')
    
    chores_csv = os.path.join(csv_dir, 'chores.csv')
    rewards_csv = os.path.join(csv_dir, 'rewards.csv')
    
    # Load and create chores from CSV
    chores_created = 0
    if os.path.exists(chores_csv):
        with open(chores_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row['title']
                points = int(row['points'])
                icon_emoji = row['icon_emoji']
                
                _, created = Chore.objects.get_or_create(
                    parent=parent,
                    title=title,
                    defaults={
                        'points': points,
                        'icon_emoji': icon_emoji,
                        'active': True
                    }
                )
                if created:
                    chores_created += 1
        print(f"Chores loaded from CSV: {chores_created} created")
    else:
        print(f"Chores CSV not found at {chores_csv}")
    
    # Load and create rewards from CSV
    rewards_created = 0
    if os.path.exists(rewards_csv):
        with open(rewards_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row['title']
                cost_points = int(row['cost_points'])
                icon_emoji = row['icon_emoji']
                
                _, created = Reward.objects.get_or_create(
                    parent=parent,
                    title=title,
                    defaults={
                        'cost_points': cost_points,
                        'icon_emoji': icon_emoji,
                        'active': True
                    }
                )
                if created:
                    rewards_created += 1
        print(f"Rewards loaded from CSV: {rewards_created} created")
    else:
        print(f"Rewards CSV not found at {rewards_csv}")
    
    print(f"Initial data created for parent: {parent.username}")


def remove_initial_data(apps, schema_editor):
    """Remove the initial chores and rewards if rolling back."""
    # We don't remove data on rollback to be safe
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_make_adjustment_reason_required'),
    ]

    operations = [
        migrations.RunPython(add_initial_data, remove_initial_data),
    ]
