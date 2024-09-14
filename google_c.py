from google.cloud import storage
from google.oauth2 import service_account
import io

# Path to your service account key file
SERVICE_ACCOUNT_FILE = 'my_flask_app/credential.json'

# Load the service account credentials
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)

# Initialize a Google Cloud Storage client using the service account credentials
client = storage.Client(credentials=credentials)

# Name of the bucket where you want to upload and download files
BUCKET_NAME = 'imageutils'
bucket = client.bucket(BUCKET_NAME)

def upload_image_on_cloud(file_io, destination_blob_name):
    """
    Uploads an image (BytesIO) to Google Cloud Storage.

    :param file_io: In-memory file (BytesIO).
    :param destination_blob_name: The name of the destination blob (object) in the bucket.
    :return: The URL of the uploaded image.
    """
    blob = bucket.blob(destination_blob_name)
    
    # Upload the in-memory file to the bucket
    blob.upload_from_file(file_io, rewind=True)  # `rewind=True` resets the BytesIO to start

    print(f"File uploaded to {destination_blob_name}.")
    return f"https://storage.googleapis.com/{BUCKET_NAME}/{destination_blob_name}"

def download_image_from_cloud(blob_name):
    """
    Downloads an image from Google Cloud Storage.

    :param blob_name: The name of the blob (object) to download from the bucket.
    :return: A BytesIO object containing the image data, or None if not found.
    """
    blob = bucket.blob(blob_name)

    if not blob.exists():
        print(f"File {blob_name} not found in cloud storage!")
        return None

    # Download the blob to a BytesIO object
    file_io = io.BytesIO()
    blob.download_to_file(file_io)
    file_io.seek(0)  # Go to the start of the BytesIO object

    return file_io

# # Example usage
# if __name__ == '__main__':
#     # Example to upload a file
#     with open('local_image.png', 'rb') as f:
#         file_io = io.BytesIO(f.read())
#     url = upload_image_on_cloud(file_io, 'uploads/local_image.png')
#     print(f"Uploaded image URL: {url}")

#     # Example to download a file
#     downloaded_file_io = download_image_from_cloud('uploads/local_image.png')
#     if downloaded_file_io:
#         with open('downloaded_image.png', 'wb') as f:
#             f.write(downloaded_file_io.getvalue())
#         print("File downloaded successfully!")
#     else:
#         print("Failed to download the file.")
