# logging
ROOT_LOG = "at_client.log"
LOG_DIR = "logs"

# Google Cloud Platform
GCP_CREDS_PATH = "config/google_service_account.json"
BUCKET_NAMES_PATH = "config/storage_bucket.json"
BUCKET_DICT_KEY = "storage_bucket"  # key to access bucket located at BUCKET_INFO_LOC

# Local directory configuration
DEFAULT_ORDER_DIR = "signals"

# Order settings
ORD_SETTINGS_PATH = "config/order_guidelines.json"
MAX_ORD_VAL_KEY = "max_order_value"
RISKY_ORD_VAL_KEY = "high_risk_order_value"
BUY_LIM_KEY = "buy_limit_percent"
SL_KEY = "SL_percentage"

# TD Ameritrade
TD_TOKEN_PATH = "config/tda_token.json"
TD_AUTH_PARAMS_PATH = "config/tda_auth_params.json"
TD_DICT_KEY_API = "tda_api_key"
TD_DICT_KEY_URI = "tda_auth_uri"
TD_DICT_KEY_ACCT = "tda_acct"

# Selenium Drivers
GECKODRIVER_PATH = "bins/geckodriver.exe"
