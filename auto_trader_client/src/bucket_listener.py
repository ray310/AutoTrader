""" Worker class that checks GCP bucket for updates
and downloads updates to local storage"""

import os
import datetime
import asyncio
from google.cloud import storage


class BucketListener:
    # need to initialize then listen (maybe with a run-like command)
    def __init__(self, gcp_bucket_name, gcp_creds_path, local_directory, sleep_time=1):
        self._gcp_creds_path = gcp_creds_path
        self._client = self._authenticate_client()
        self._bucket_name = gcp_bucket_name
        self._updated = datetime.datetime.now(datetime.timezone.utc)
        self._local_directory = local_directory
        self._sleep_time = sleep_time
        self._init_local_directory(self._local_directory)

    def _authenticate_client(self):
        return storage.Client.from_service_account_json(self._gcp_creds_path)

    def _init_local_directory(self, local_directory):
        os.makedirs(local_directory, exist_ok=True)

    def _get_newest(self):
        blob_iter = self._client.list_blobs(self._bucket_name)
        recent = self._updated - datetime.timedelta(seconds=10)
        for blob in blob_iter:
            if blob.time_created > recent:
                file_name = os.path.join(self._local_directory, blob.name)
                if not os.path.isfile(file_name):
                    blob.download_to_filename(file_name)
        self._updated = datetime.datetime.now(datetime.timezone.utc)

    async def run(self):
        while True:
            self._get_newest()
            await asyncio.sleep(self._sleep_time)
