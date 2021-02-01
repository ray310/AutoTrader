""" Worker class that checks GCP bucket for updates
and downloads updates to local storage"""

import os
import asyncio
import datetime


class OrderMonitor:
    """Monitors local directory for updates
    and generates an order when an update is received"""
    def __init__(self, order_directory, sleep_time=1):
        self._order_directory = order_directory
        self._sleep_time = sleep_time
        self._orders = set()
        self._last_check = datetime.datetime.now(datetime.timezone.utc)

    def _check_new_files(self):
        """Check order directory for new files"""
        files = [f for f in os.listdir(self._order_directory)]
        for f in files:
            if (
                self._get_file_creation_time(self._order_directory, f)
                > self._last_check
            ):
                if os.path.isfile(os.path.join(self._order_directory, f)):
                    self._process_new_file(f)
        self._last_check = datetime.datetime.now(datetime.timezone.utc)

    def _process_new_file(self, file):
        """Process new file"""
        if file not in self._orders:
            f_name, f_ext = os.path.splitext(file)
            if f_ext == ".json":
                self._generate_order(file)
            self._orders.add(file)

    def _generate_order(self, file):
        """Process possibly valid order"""
        print(f"{file} generated")
        # TODO: Need to implement order validation and generation

    async def run(self):
        while True:
            print("monitoring")
            self._check_new_files()
            await asyncio.sleep(self._sleep_time)

    @staticmethod
    def _get_file_creation_time(directory, file):
        """Returns time file was created on Windows systems or
        time the file was last modified on UNIX-like systems"""
        # using mtime on UNIX-like because
        # ctime reflects changes to metadata like permissions
        if os.name == "posix":
            timestamp = os.path.getmtime(os.path.join(directory, file))
            return datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
        elif os.name == "nt":
            # ctime on Windows systems as it reflects actual creation time
            timestamp = os.path.getctime(os.path.join(directory, file))
            return datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
        else:
            raise OSError("OS does not appear to be Windows or UNIX-like")
