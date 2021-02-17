""" General utilities """


def init_root_logger(log_filename, log_directory="logs", log_level=10):
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


def get_env_var_value(env_var_key):
    import os

    try:
        if os.environ[env_var_key] == "":
            raise ValueError(f"ENVIRONMENT VARIABLE: {env_var_key} :SET TO ''")
        else:
            return os.environ[env_var_key]
    except KeyError:
        msg = f"ENVIRONMENT VARIABLE: {env_var_key} :NOT FOUND"
        raise KeyError(msg) from None
