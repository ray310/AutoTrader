"""Server driver """
import json
import src.gcp_utils as gcp_utils
import src.server_utils as log_utils
import src.discord_bot as discord_bot
from src.server_settings import (
    BASE_LOG,
    ENV_KEY_KEYS_BUCKET,
    ENV_KEY_BUCKET,
    DISCORD_TOKEN_LOC,
    DISCORD_TOKEN_KEY,
    AUTHOR,
)
from src.server_utils import get_env_var_value


def main():
    # initiate logging
    log_file_name = BASE_LOG
    log_utils.init_root_logger(log_file_name)

    # get storage buckets from environmental variables
    keys_bucket = get_env_var_value(ENV_KEY_KEYS_BUCKET)
    bucket = get_env_var_value(ENV_KEY_BUCKET)

    # get discord bot token
    bot_token_bytes = gcp_utils.get_gcp_blob(keys_bucket, DISCORD_TOKEN_LOC)
    bot_token = json.loads(bot_token_bytes)[DISCORD_TOKEN_KEY]

    # start discord listener bot
    bot = discord_bot.ListenerBot(bucket, author=AUTHOR)
    bot.run(bot_token)


if __name__ == "__main__":
    main()
