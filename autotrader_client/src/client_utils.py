""" General utilities """


# TODO: this is copied from server_utils. Consolidate function to one location
def init_root_logger(log_filename, log_directory="logs", log_level=20):
    """Starts logger at specified location with specified formatting"""
    import logging
    import os
    import time

    os.makedirs(log_directory, exist_ok=True)
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(
        filename=os.path.join(log_directory, log_filename),
        level=log_level,
        format="%(levelname)s: %(message)s: %(asctime)s%(msecs)d",
        datefmt="%m/%d/%Y %H:%M:%S",
    )
