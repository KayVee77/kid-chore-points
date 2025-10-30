"""
Custom storage backends for Azure Blob Storage.
Separates static files and media files into different containers.
"""
from storages.backends.azure_storage import AzureStorage
import os


class AzureMediaStorage(AzureStorage):
    """Storage for user-uploaded media files."""
    account_name = os.environ.get('AZURE_ACCOUNT_NAME')
    account_key = os.environ.get('AZURE_ACCOUNT_KEY')
    azure_container = 'media'
    expiration_secs = None


class AzureStaticStorage(AzureStorage):
    """Storage for static files (CSS, JS, images)."""
    account_name = os.environ.get('AZURE_ACCOUNT_NAME')
    account_key = os.environ.get('AZURE_ACCOUNT_KEY')
    azure_container = 'static'
    expiration_secs = None
