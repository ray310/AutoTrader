"""Google Cloud Platform (GCP) utility functions for auto_trader_server"""


def download_gcp_blob(bucket_name, source_blob_name, dest_file_name):
    """Downloads a blob from the GCP bucket to destination file name"""
    from google.cloud import storage

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(dest_file_name)


def get_gcp_blob(bucket_name, source_blob_name):
    """Gets a blob as bytes object from the GCP bucket"""
    from google.cloud import storage

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    bytes_obj = blob.download_as_bytes()
    return bytes_obj


def upload_string_as_gcp_blob(bucket_name, string, dest_blob_name):
    """Uploads a string as a blob to the GCP bucket"""
    from google.cloud import storage

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(dest_blob_name)
    blob.upload_from_string(string)
