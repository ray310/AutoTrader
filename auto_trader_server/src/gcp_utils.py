"""Google Cloud Platform (GCP) utility functions for auto_trader_server"""


def download_gcp_blob(bucket_name: str, source_blob_name: str, dest_file_name: str):
    """Downloads a blob from the GCP bucket to destination file name"""
    from google.cloud import storage

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(dest_file_name)


def get_gcp_blob(bucket_name: str, source_blob_name: str):
    """Gets a blob as bytes object from the GCP bucket"""
    from google.cloud import storage

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    bytes_obj = blob.download_as_bytes()
    return bytes_obj


def upload_as_gcp_blob(bucket_name: str, dictionary: dict, dest_blob_name: str):
    """Uploads a string as a blob to the GCP bucket"""
    import os
    import json
    from google.cloud import storage

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(dest_blob_name)

    name, ext = os.path.splitext(dest_blob_name)
    if ext == ".json":
        with open(dest_blob_name, "w+") as fp:
            json.dump(dictionary, fp)
        blob.upload_from_filename(dest_blob_name, content_type="application/json")
    else:
        blob.upload_from_string(str(dictionary))
