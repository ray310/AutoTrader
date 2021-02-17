import datetime
from discord.ext import commands
import src.gcp_utils as utils
import src.text_to_order_params as ttop


class ListenerBot(commands.Bot):
    """Listener bot. If author is provided, then listener will exclusively listen
    listen for messages from that author (user_id)"""

    def __init__(self, storage_bucket, command_prefix="%%", author=None):
        super().__init__(command_prefix)
        self.storage_bucket = storage_bucket
        self.author = author

    async def on_message(self, message, author=None):
        order_params = ttop.text_to_order_params(message.content)
        if order_params is not None:
            dt_stamp = datetime.datetime.strftime(
                datetime.datetime.now(datetime.timezone.utc), "%d-%b-%y_%H_%M_%S"
            )
            blob_name = order_params["ticker"] + dt_stamp + ".json"
            utils.upload_as_gcp_blob(self.storage_bucket, order_params, blob_name)
