from google.cloud import storage
from google.api_core.page_iterator import Iterator

def blob_exists(blob_name: str, bucket_name: str) -> bool:
    """
    Check if a file/blob exists in a Google Cloud Storage bucket.

    Args:
        blob_name (str): Name of the file/blob to check.
        bucket_name (str): Name of the bucket to search in.

    Returns:
        bool: True if the blob exists, False if not.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.exists()

def upload_to_bucket(blob_name: str, data: str | bytes, bucket_name: str, content_type: str = 'text/csv') -> None:
    """
    Upload data to a Google Cloud Storage bucket.

    Args:
        blob_name (str): Name of the blob/file to create or overwrite.
        data (str | bytes): Data to upload, either as a string or bytes.
        bucket_name (str): Name of the bucket to upload to.
        content_type (str, optional): MIME type of the data. Defaults to 'text/csv'.

    Returns:
        None
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(data, content_type=content_type)


def download_from_bucket(blob_name: str, bucket_name: str, file_name: str) -> None:
    """
    Download a blob/file from a Google Cloud Storage bucket to a local file.

    Args:
        blob_name (str): Name of the blob to download.
        bucket_name (str): Name of the bucket containing the blob.
        file_name (str): Local file path to save the downloaded blob.

    Returns:
        None
    """
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(file_name)
    

def download_from_bucket_as_bytes(blob_name, bucket_name) -> bytes:
    """
    Download a blob/file from a Google Cloud Storage bucket as bytes.

    Args:
        blob_name (str): Name of the blob to download.
        bucket_name (str): Name of the bucket containing the blob.

    Returns:
        bytes: The downloaded blob content as bytes.
    """
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.download_as_bytes()


def list_bucket_contents(bucket_name: str) -> Iterator:
    """
    List all blobs/files in a Google Cloud Storage bucket.

    Args:
        bucket_name (str): Name of the bucket to list contents from.

    Returns:
        Iterator: An iterator over the blobs in the bucket.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    return bucket.list_blobs()
    