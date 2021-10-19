import os
from tr4d3r.backend.robinhood import (
    RobinhoodRealMarket,
    RobinhoodRealPortfolio,
)
from tr4d3r.core.trading import RealTimeEquilibrium
from tr4d3r.core.notification import TelegramChat

LOCAL_DIR = os.path.dirname(__file__)
FOLIO_PATH_ROOT = os.path.join(LOCAL_DIR, "folio.json")
FOLIO_PATH_LATEST = f"{FOLIO_PATH_ROOT}.latest"
CHAT_MESSAGE_PREFIX = '*Autopilot*'


def get_portfolio():
    return RobinhoodRealPortfolio.load_json(FOLIO_PATH_LATEST)

def get_manager():
    manager = RealTimeEquilibrium(
        equilibrium = {
            'SPY': 0.4,
            'BABA': 0.1,
            'BILI': 0.1,
            'AAPL': 0.1,
         },
    )
    return manager

def get_chat():
    return TelegramChat(
        bot_config={'token': os.environ['TG_BOT_TOKEN']},
        client_config={'chat_id': os.environ['TG_CHAT_ID']},
    )
