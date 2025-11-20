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
    overwrite_files = True  # Allow overwriting existing files
    
    def get_available_name(self, name, max_length=None):
        """
        Return the name as-is to allow overwriting.
        By default, Django appends random strings to avoid conflicts.
        """
        if self.overwrite_files:
            return name
        return super().get_available_name(name, max_length)


class AzureStaticStorage(AzureStorage):
    """Storage for static files (CSS, JS, images)."""
    account_name = os.environ.get('AZURE_ACCOUNT_NAME')
    account_key = os.environ.get('AZURE_ACCOUNT_KEY')
    azure_container = 'static'
    expiration_secs = None
    overwrite_files = True
