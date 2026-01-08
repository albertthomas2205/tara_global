import os
import uuid
import requests

class BunnyCDNUploader:
    def __init__(self, api_key, storage_zone, base_url):
        self.api_key = api_key
        self.storage_zone = storage_zone
        self.base_url = base_url.rstrip('/')
        self.folder = "tara-images"  # Your specified folder
        self.api_url = f"https://storage.bunnycdn.com/{self.storage_zone}/{self.folder}/"
        self.headers = {
            "AccessKey": self.api_key,
            "Content-Type": "application/octet-stream"
        }

    def upload_file(self, file):
        if not file:
            return None

        # Generate unique filename
        _, ext = os.path.splitext(file.name)
        unique_filename = f"{uuid.uuid4().hex}{ext.lower()}"
        upload_url = f"{self.api_url}{unique_filename}"
        print(f"Uploading to: {upload_url}")

        try:
            # Read file content (works for InMemoryUploadedFile and TemporaryUploadedFile)
            file_content = file.read()
            file.seek(0)  # Reset pointer just in case

            # Upload to BunnyCDN
            response = requests.put(
                upload_url,
                headers=self.headers,
                data=file_content,
                timeout=30
            )

            if response.status_code == 201:
                final_url = f"{self.base_url}/{self.folder}/{unique_filename}"
                print(f"✅ Upload successful: {final_url}")
                return final_url
            else:
                print(f"❌ Upload failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"⚠️ Upload error: {str(e)}")
            return None
    def delete_file(self, file_url):
        """
        Delete a file from BunnyCDN given its full URL.
        Returns True if deleted successfully, False otherwise.
        """
        if not file_url:
            return False

        # Extract the relative path from the full URL
        if file_url.startswith(self.base_url):
            relative_path = file_url.replace(self.base_url, "").lstrip("/")
        else:
            relative_path = file_url

        url = f"https://storage.bunnycdn.com/{self.storage_zone}/{relative_path}"
        headers = {"AccessKey": self.api_key}

        try:
            response = requests.delete(url, headers=headers)
            return response.status_code in [200, 204]
        except Exception:
            return False
