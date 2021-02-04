""" Worker class that monitors local directory for new order signals. New order signals
are validated and if valid, generate order"""


import os
import json
import asyncio
import datetime
import src.validate_params as vp


class OrderMonitor:
    """Monitors local directory for updates
    and generates an order when an update is received"""

    def __init__(self, order_directory, sleep_time=1, order_ext="json"):
        self._order_dir = order_directory
        self._sleep_time = sleep_time
        self._order_ext = order_ext
        self._directory_content = set()
        self._last_check = datetime.datetime.now(datetime.timezone.utc)

    def _check_new_files(self):
        """Check order directory for new files"""
        new_orders = []
        files = [f for f in os.listdir(self._order_dir)]
        for f in files:
            if self._get_creation_time(self._order_dir, f) > self._last_check:
                if self._is_new_order_file(f):
                    new_orders.append(f)
                self._directory_content.add(f)
        self._last_check = datetime.datetime.now(datetime.timezone.utc)
        return new_orders

    def _is_new_order_file(self, file):
        """Return True if file is a new file with valid file extension, else False"""
        new_file = False
        if os.path.isfile(os.path.join(self._order_dir, file)):
            if file not in self._directory_content:
                if os.path.splitext(file)[-1] == self._order_ext:
                    new_file = True
        return new_file

    async def run(self):
        while True:
            print("monitoring")
            new_files = self._check_new_files()
            for f in new_files:
                self._process_order(self._order_dir, f)
            await asyncio.sleep(self._sleep_time)

    @staticmethod
    def _get_creation_time(directory, file_like):
        """Returns time file was created on Windows systems or
        time the file was last modified on UNIX-like systems"""
        # using mtime on UNIX-like because
        # ctime reflects changes to metadata like permissions
        if os.name == "posix":
            timestamp = os.path.getmtime(os.path.join(directory, file_like))
            return datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
        elif os.name == "nt":
            # ctime on Windows systems as it reflects actual creation time
            timestamp = os.path.getctime(os.path.join(directory, file_like))
            return datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
        else:
            raise OSError("OS does not appear to be Windows or UNIX-like")

    @staticmethod
    def _process_order(directory, file):
        """Validate and attempt to place order"""
        with open(os.path.join(directory, file)) as f:
            order_params = json.load(file)
        is_valid = vp.validate_params(order_params)
        if is_valid:
            valid_params = vp.reformat_params(order_params)
            # td.generate_order(valid_params)"""  # TODO: implement
        print(f"{file} processed")
