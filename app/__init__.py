import os
import tracemalloc

from dotenv import load_dotenv


﻿API_ID = 29916910

API_HASH = "4d1a40cb4722a0b1a8289b705b6a2228"

BOT_TOKEN = "6398685157:AAGKnMJm3oRHxavLY-MHbXTVa4HeDu_7H-E"

load_dotenv("config.env")
tracemalloc.start()


# isort: skip
from app.config import Config  # NOQA
from app.core import LOGGER, Message  # NOQA
from app.core.client.client import BOT  # NOQA

if "com.termux" not in os.environ.get("PATH", ""):
    import uvloop  # isort:skip

    uvloop.install()

bot: BOT = BOT()
