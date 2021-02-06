# logging
ROOT_LOG = "at_client.log"
LOG_DIR = "logs"

# Google Cloud Platform
GCP_CREDS_PATH = "config/google_service_account.env"
BUCKET_NAMES_PATH = "config/storage_bucket.json"
BUCKET_DICT_KEY = "storage_bucket"  # key to access bucket located at BUCKET_INFO_LOC

# Local directory configuration
DEFAULT_ORDER_DIR = "signals"

# Order settings
ORDER_SETTINGS_FILE = "config/order_guidelines.json"
SL_PERCENT_KEY = "SL_percentage"
ORDER_VAL_KEY = "order_value"

# TD Ameritrade
TD_TOKEN_PATH = "config/tda_token.json"
TD_AUTH_PARAMS_PATH = "config/tda_auth_params.json"
TD_DICT_KEY_API = "tda_api_key"
TD_DICT_KEY_URI = "tda_auth_uri"
TD_DICT_KEY_ACCT = "tda_acct"

# Selenium Drivers
GECKODRIVER_PATH = "bins/geckodriver.exe"
