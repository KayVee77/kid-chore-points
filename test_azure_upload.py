"""
Test Azure Blob Storage upload to diagnose photo upload issue.
Run this to verify Azure credentials and storage access work.
"""
import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Load environment variables (for local testing)
load_dotenv()

# Get Azure credentials
AZURE_ACCOUNT_NAME = os.environ.get('AZURE_ACCOUNT_NAME', 'chorepointsstorage')
AZURE_ACCOUNT_KEY = os.environ.get('AZURE_ACCOUNT_KEY')

if not AZURE_ACCOUNT_KEY:
    print("❌ ERROR: AZURE_ACCOUNT_KEY not set in environment variables!")
    print("Set it in Azure App Service > Configuration > Application settings")
    exit(1)

# Create connection string
connection_string = f"DefaultEndpointsProtocol=https;AccountName={AZURE_ACCOUNT_NAME};AccountKey={AZURE_ACCOUNT_KEY};EndpointSuffix=core.windows.net"

print(f"🔍 Testing Azure Blob Storage connection...")
print(f"   Account: {AZURE_ACCOUNT_NAME}")
print(f"   Container: media")

try:
    # Create BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
    # Get container client
    container_client = blob_service_client.get_container_client('media')
    
    # Check if container exists
    if container_client.exists():
        print(f"✅ Container 'media' exists")
    else:
        print(f"❌ Container 'media' does NOT exist!")
        print(f"   Create it in Azure Portal > Storage Account > Containers")
        exit(1)
    
    # Try uploading a test file
    test_data = b"Test upload from chorepoints app"
    blob_name = "kid_avatars/test_upload.txt"
    blob_client = container_client.get_blob_client(blob_name)
    
    print(f"📤 Uploading test file: {blob_name}")
    blob_client.upload_blob(test_data, overwrite=True)
    print(f"✅ Upload successful!")
    
    # Verify file exists
    url = blob_client.url
    print(f"📍 File URL: {url}")
    
    # Try downloading to verify
    download_stream = blob_client.download_blob()
    downloaded_data = download_stream.readall()
    
    if downloaded_data == test_data:
        print(f"✅ Download successful - file content matches!")
    else:
        print(f"❌ Download failed or content mismatch")
    
    # Clean up test file
    blob_client.delete_blob()
    print(f"🗑️ Cleaned up test file")
    
    print("\n✅ Azure Blob Storage is working correctly!")
    print("❓ Issue is likely in Django storage backend configuration or file handling")

except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    print(f"   Check Azure credentials and network connectivity")
    exit(1)
