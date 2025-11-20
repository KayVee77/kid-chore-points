#!/usr/bin/env python
"""
Quick script to test if django-storages is installed and working on Azure.
Run this via: az webapp ssh --name elija-agota --resource-group chorepoints-rg-us
Then: cd /home/site/wwwroot && python test_storage.py
"""
import os
import sys

print("=" * 60)
print("AZURE STORAGE CONFIGURATION TEST")
print("=" * 60)

# Check if running on Azure
print(f"\n1. Python version: {sys.version}")
print(f"2. Current directory: {os.getcwd()}")

# Check environment variables
print("\n3. Environment Variables:")
print(f"   DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE', 'NOT SET')}")
print(f"   AZURE_ACCOUNT_NAME: {os.environ.get('AZURE_ACCOUNT_NAME', 'NOT SET')}")
print(f"   AZURE_ACCOUNT_KEY: {'SET (hidden)' if os.environ.get('AZURE_ACCOUNT_KEY') else 'NOT SET'}")

# Try to import django-storages
print("\n4. Checking django-storages installation:")
try:
    import storages
    print(f"   ✅ django-storages is INSTALLED")
    print(f"   Version: {storages.__version__ if hasattr(storages, '__version__') else 'unknown'}")
except ImportError as e:
    print(f"   ❌ django-storages is NOT INSTALLED")
    print(f"   Error: {e}")
    sys.exit(1)

# Try to import Django settings
print("\n5. Loading Django settings:")
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chorepoints.settings_production')
    import django
    django.setup()
    from django.conf import settings
    print(f"   ✅ Django loaded successfully")
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
except Exception as e:
    print(f"   ❌ Failed to load Django: {e}")
    sys.exit(1)

# Try to test storage connection
print("\n6. Testing Azure Blob Storage connection:")
try:
    from django.core.files.storage import default_storage
    print(f"   Storage class: {default_storage.__class__.__name__}")
    print(f"   Storage module: {default_storage.__class__.__module__}")
    
    # Try to check if we can connect
    if hasattr(default_storage, 'account_name'):
        print(f"   Account name: {default_storage.account_name}")
        print(f"   Container: {default_storage.azure_container if hasattr(default_storage, 'azure_container') else 'N/A'}")
    
    # Try listing files (won't work if connection fails)
    try:
        dirs, files = default_storage.listdir('')
        print(f"   ✅ Successfully connected to Azure Blob Storage")
        print(f"   Root directories: {dirs}")
    except Exception as e:
        print(f"   ⚠️  Could not list files: {e}")
        
except Exception as e:
    print(f"   ❌ Storage test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("TEST COMPLETED")
print("=" * 60)
