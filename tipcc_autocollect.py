from asyncio import TimeoutError, sleep
from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    Formatter,
    StreamHandler,
    getLogger,
)
from math import acosh, asinh, atanh, ceil, cos, cosh, e, erf, exp
from math import fabs as abs
from math import factorial, floor
from math import fmod as mod
from math import (
    gamma,
    gcd,
    hypot,
    log,
    log1p,
    log2,
    log10,
    pi,
    pow,
    sin,
    sinh,
    sqrt,
    tan,
    tau,
)
from random import randint, uniform
from re import compile
from time import time
from urllib.parse import quote, unquote

from aiohttp import ClientSession
from art import tprint
from discord import Client, HTTPException, LoginFailure, Message, NotFound, Status
from discord.ext import tasks
from questionary import checkbox, select, text

# Add these imports at the top of your existing script
import requests
import logging
from datetime import datetime

# Add this custom logging handler class
class TelegramLoggingHandler(logging.Handler):
    def __init__(self, bot_token, chat_id, keyword="Entered"):
        super().__init__()
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.keyword = keyword.lower()
        self.telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    def emit(self, record):
        """Called whenever a log message is emitted"""
        try:
            # Format the log message
            log_message = self.format(record)

            # Check if keyword exists in the log message
            if self.keyword in log_message.lower():
                self.send_telegram_message(log_message)
        except Exception as e:
            print(f"Error in TelegramLoggingHandler: {e}")

    def send_telegram_message(self, log_message):
        """Send the log message to Telegram"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            telegram_message = f"🚨 <b>Keyword Alert: {self.keyword.title()}</b> 🚨\n\n"
            telegram_message += f"<b>Time:</b> {timestamp}\n"
            telegram_message += f"<b>Log Message:</b>\n<code>{log_message}</code>"

            payload = {
                'chat_id': self.chat_id,
                'text': telegram_message,
                'parse_mode': 'HTML'
            }

            response = requests.post(self.telegram_url, data=payload)
            if response.status_code == 200:
                print("✅ Telegram notification sent!")
            else:
                print(f"❌ Failed to send Telegram message: {response.text}")

        except Exception as e:
            print(f"❌ Error sending Telegram message: {e}")

# Configuration - Replace with your actual values
BOT_TOKEN = "8043331214:AAHDVSwrNVAK2UGh1UwPHbLFt7wBgPKHbZA"
CHAT_ID = "6931323094"
KEYWORD = "Entered"  # The keyword to monitor for

# Set up the Telegram handler
def setup_telegram_logging():
    """Add Telegram handler to your existing logger"""
    # Create the Telegram handler
    telegram_handler = TelegramLoggingHandler(BOT_TOKEN, CHAT_ID, KEYWORD)

    # Set the same format as your existing logs (optional)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(name)s %(message)s')
    telegram_handler.setFormatter(formatter)

    # Add handler to the root logger (this catches all logging)
    root_logger = logging.getLogger()
    root_logger.addHandler(telegram_handler)

    # Or if you have a specific logger name, use that instead:
    # specific_logger = logging.getLogger('tipcc_autocollect')
    # specific_logger.addHandler(telegram_handler)

# SETUP INSTRUCTIONS:
# 1. Replace BOT_TOKEN and CHAT_ID with your actual values
# 2. Add this line somewhere in your script after logging is configured:
#    setup_telegram_logging()
# 
# That's it! Now whenever your script logs something with "Entered",
# it will automatically send a Telegram notification.

# Alternative: If you want to add it to a specific logger only
def setup_specific_logger_telegram(logger_name='tipcc_autocollect'):
    """Add Telegram handler to a specific logger"""
    telegram_handler = TelegramLoggingHandler(BOT_TOKEN, CHAT_ID, KEYWORD)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(name)s %(message)s')
    telegram_handler.setFormatter(formatter)

    # Get your specific logger and add the handler
    logger = logging.getLogger(logger_name)
    logger.addHandler(telegram_handler)

# Example usage in your main code:
if __name__ == "__main__":
    # Your existing logging setup goes here first
    # Then add this line:
    setup_telegram_logging()

    # Now your script runs normally and will send Telegram notifications
    # when "Entered" appears in any log message

class ColourFormatter(
    Formatter
):  # Taken from discord.py-self and modified to my liking.

    LEVEL_COLOURS = [
        (DEBUG, "\x1b[40;1m"),
        (INFO, "\x1b[34;1m"),
        (WARNING, "\x1b[33;1m"),
        (ERROR, "\x1b[31m"),
        (CRITICAL, "\x1b[41m"),
    ]

    FORMATS = {
        level: Formatter(
            f"\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m \x1b[35m%(name)s\x1b[0m %(message)s \x1b[30;1m(%(filename)s:%(lineno)d)\x1b[0m",
            "%d-%b-%Y %I:%M:%S %p",
        )
        for level, colour in LEVEL_COLOURS
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[DEBUG]

        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f"\x1b[31m{text}\x1b[0m"

        output = formatter.format(record)

        record.exc_text = None
        return output


handler = StreamHandler()
formatter = ColourFormatter()

handler.setFormatter(formatter)
logger = getLogger("tipcc_autocollect")
logger.addHandler(handler)
logger.setLevel("INFO")


def cbrt(x):
    return pow(x, 1 / 3)


try:
    from ujson import dump, load
except ModuleNotFoundError:
    logger.warning("ujson not found, using json instead.")
    from json import dump, load
except ImportError:
    logger.warning("ujson not found, using json instead.")
    from json import dump, load
else:
    logger.info("ujson found, using ujson.")


channel = None


print("\033[0;35m")
tprint("QuartzWarrior", font="smslant")
print("\033[0m")

try:
    with open("config.json", "r") as f:
        config = load(f)
except FileNotFoundError:
    config = {
        "TOKEN": "",
        "PRESENCE": "invisible",
        "CPM": [200, 310],
        "FIRST": True,
        "id": 0,
        "channel_id": 0,
        "TARGET_AMOUNT": 0.0,
        "SMART_DELAY": True,
        "RANGE_DELAY": False,
        "DELAY": [0, 1],
        "BANNED_WORDS": ["bot", "ban"],
        "MESSAGES": [],
        "WHITELIST": [],
        "BLACKLIST": [],
        "CHANNEL_WHITELIST": [],
        "CHANNEL_BLACKLIST": [],
        "IGNORE_USERS": [],
        "SEND_MESSAGE": False,
        "WHITELIST_ON": False,
        "BLACKLIST_ON": False,
        "CHANNEL_WHITELIST_ON": False,
        "CHANNEL_BLACKLIST_ON": False,
        "IGNORE_DROPS_UNDER": 0.0,
        "IGNORE_TIME_UNDER": 0.0,
        "IGNORE_THRESHOLDS": [],
        "DISABLE_AIRDROP": False,
        "DISABLE_TRIVIADROP": False,
        "DISABLE_MATHDROP": False,
        "DISABLE_PHRASEDROP": False,
        "DISABLE_REDPACKET": False,
        "DELAY_AIRDROP": True,
        "DELAY_TRIVIADROP": True,
        "DELAY_MATHDROP": True,
        "DELAY_PHRASEDROP": True,
        "DELAY_REDPACKET": False,
    }
    with open("config.json", "w") as f:
        dump(config, f, indent=4)

token_regex = compile(r"[\w-]{24}\.[\w-]{6}\.[\w-]{27,}")
decimal_regex = compile(r"^-?\d+(?:\.\d+)$")


def validate_token(token):
    if token_regex.search(token):
        return True
    else:
        return False


def validate_decimal(decimal):
    if decimal_regex.match(decimal):
        return True
    else:
        return False


def validate_threshold_chance(s):
    try:
        threshold, chance = s.split(":")
        return (
            validate_decimal(threshold)
            and chance.isnumeric()
            and 0 <= int(chance) <= 100
        )
    except ValueError:
        if s == "":
            return True
        return False


if config["TOKEN"] == "":
    token_input = text(
        "What is your discord token?",
        qmark="->",
        validate=lambda x: validate_token(x),
    ).ask()
    if token_input is not None:
        config["TOKEN"] = token_input
        with open("config.json", "w") as f:
            dump(config, f, indent=4)
        logger.debug("Token saved.")

if config["FIRST"] == True:
    config["PRESENCE"] = select(
        "What do you want your presence to be?",
        choices=[
            "online",
            "idle",
            "dnd",
            "invisible",
        ],
        default="invisible",
        qmark="->",
    ).ask()
    config["CPM"][0] = int(
        text(
            "What is your minimum CPM (Characters Per Minute)?\nThis is to make the phrase drop collector more legit.\nRemember, the higher the faster!",
            default="200",
            qmark="->",
            validate=lambda x: (validate_decimal(x) or x.isnumeric()) and float(x) >= 0,
        ).ask()
    )
    config["CPM"][1] = int(
        text(
            "What is your maximum CPM (Characters Per Minute)?\nThis is to make the phrase drop collector more legit.\nRemember, the higher the faster!",
            default="310",
            qmark="->",
            validate=lambda x: (validate_decimal(x) or x.isnumeric()) and float(x) >= 0,
        ).ask()
    )
    config["FIRST"] = False
    config["DISABLE_AIRDROP"] = False
    config["DISABLE_TRIVIADROP"] = False
    config["DISABLE_MATHDROP"] = False
    config["DISABLE_PHRASEDROP"] = False
    config["DISABLE_REDPACKET"] = False
    config["DELAY_AIRDROP"] = True
    config["DELAY_TRIVIADROP"] = True
    config["DELAY_MATHDROP"] = True
    config["DELAY_PHRASEDROP"] = True
    config["DELAY_REDPACKET"] = False
    disable_drops = checkbox(
        "What drop types do you want to disable? (Leave blank for none)",
        choices=[
            "airdrop",
            "triviadrop",
            "mathdrop",
            "phrasedrop",
            "redpacket",
        ],
        qmark="->",
    ).ask()
    if not disable_drops:
        disable_drops = []
    if "airdrop" in disable_drops:
        config["DISABLE_AIRDROP"] = True
    if "triviadrop" in disable_drops:
        config["DISABLE_TRIVIADROP"] = True
    if "mathdrop" in disable_drops:
        config["DISABLE_MATHDROP"] = True
    if "phrasedrop" in disable_drops:
        config["DISABLE_PHRASEDROP"] = True
    if "redpacket" in disable_drops:
        config["DISABLE_REDPACKET"] = True
    delay_drops = checkbox(
        "What drop types do you want to enable delay for? (Leave blank for none)",
        choices=[
            "airdrop",
            "triviadrop",
            "mathdrop",
            "phrasedrop",
            "redpacket",
        ],
        qmark="->",
    ).ask()
    if not delay_drops:
        delay_drops = []
    if "airdrop" in delay_drops:
        config["DELAY_AIRDROP"] = True
    if "triviadrop" in delay_drops:
        config["DELAY_TRIVIADROP"] = True
    if "mathdrop" in delay_drops:
        config["DELAY_MATHDROP"] = True
    if "phrasedrop" in delay_drops:
        config["DELAY_PHRASEDROP"] = True
    if "redpacket" in delay_drops:
        config["DELAY_REDPACKET"] = True
    ignore_drops_under = text(
        "What is the minimum amount of money you want to ignore?",
        default="0",
        qmark="->",
        validate=lambda x: ((validate_decimal(x) or x.isnumeric()) and float(x) >= 0)
        or x == "",
    ).ask()
    if ignore_drops_under != "":
        config["IGNORE_DROPS_UNDER"] = float(ignore_drops_under)
    else:
        config["IGNORE_DROPS_UNDER"] = 0.0
    ignore_time_under = text(
        "What is the minimum time you want to ignore?",
        default="0",
        qmark="->",
        validate=lambda x: ((validate_decimal(x) or x.isnumeric()) and float(x) >= 0)
        or x == "",
    ).ask()
    if ignore_time_under != "":
        config["IGNORE_TIME_UNDER"] = float(ignore_time_under)
    else:
        config["IGNORE_TIME_UNDER"] = 0.0
    ignore_thresholds = text(
        "Enter your ignore thresholds and chances in the format 'threshold:chance', separated by commas (e.g. '0.10:10,0.20:20')",
        validate=lambda x: all(validate_threshold_chance(pair) for pair in x.split(","))
        or x == "",
        default="",
        qmark="->",
    ).ask()
    if ignore_thresholds != "":
        config["IGNORE_THRESHOLDS"] = [
            {"threshold": float(pair.split(":")[0]), "chance": int(pair.split(":")[1])}
            for pair in ignore_thresholds.split(",")
        ]
    else:
        config["IGNORE_THRESHOLDS"] = []
    smart_delay = select(
        "Do you want to enable smart delay? (This will make the bot wait for the drop to end before claiming it)",
        choices=["yes", "no"],
        qmark="->",
    ).ask()
    if smart_delay == "yes":
        config["SMART_DELAY"] = True
    else:
        config["SMART_DELAY"] = False
        range_delay = select(
            "Do you want to enable range delay? (This will make the bot wait for a random delay between two values)",
            choices=["yes", "no"],
            qmark="->",
        ).ask()
        if range_delay == "yes":
            config["RANGE_DELAY"] = True
            min_delay = text(
                "What is the minimum delay you want to use in seconds?",
                validate=lambda x: (validate_decimal(x) or x.isnumeric()) and float(x) >= 0,
                qmark="->",
            ).ask()
            max_delay = text(
                "What is the maximum delay you want to use in seconds?",
                validate=lambda x: (validate_decimal(x) or x.isnumeric()) and float(x) >= 0,
                qmark="->",
            ).ask()
            config["DELAY"] = [float(min_delay), float(max_delay)]
        else:
            manual_delay = text(
                "What is the delay you want to use in seconds? (Leave blank for none)",
                validate=lambda x: (validate_decimal(x) or x.isnumeric()) or x == "",
                default="0",
                qmark="->",
            ).ask()
            if manual_delay != "":
                config["DELAY"] = [float(manual_delay), float(manual_delay)]
            else:
                config["DELAY"] = [0, 0]
    banned_words = text(
        "What words do you want to ban? Seperate each word with a comma.",
        validate=lambda x: len(x) > 0 or x == "",
        qmark="->",
    ).ask()
    if not banned_words:
        banned_words = []
    else:
        banned_words = banned_words.split(",")
    config["BANNED_WORDS"] = banned_words
    send_messages = select(
        "Do you want to send messages after claiming a drop?",
        choices=["yes", "no"],
        qmark="->",
    ).ask()
    config["SEND_MESSAGE"] = send_messages == "yes"
    if config["SEND_MESSAGE"]:
        messages = text(
            "What messages do you want to send after claiming a drop? Seperate each message with a comma.",
            validate=lambda x: len(x) > 0 or x == "",
            qmark="->",
        ).ask()
        if not messages:
            messages = []
        else:
            messages = messages.split(",")
        config["MESSAGES"] = messages
    enable_whitelist = select(
        "Do you want to enable whitelist? (This will only enter drops in the servers you specify)",
        choices=["yes", "no"],
        qmark="->",
    ).ask()
    config["WHITELIST_ON"] = enable_whitelist == "yes"
    if not config["WHITELIST_ON"]:
        enable_blacklist = select(
            "Do you want to enable blacklist? (This will ignore drops in the servers you specify)",
            choices=["yes", "no"],
            qmark="->",
        ).ask()
        config["BLACKLIST_ON"] = enable_blacklist == "yes"
        if config["BLACKLIST_ON"]:
            blacklist = text(
                "What servers do you want to blacklist? Seperate each server ID with a comma.",
                validate=lambda x: (
                    len(x) > 0
                    and all(y.isnumeric() and 17 <= len(y) <= 19 for y in x.split(","))
                )
                or x == "",
                qmark="->",
            ).ask()
            if not blacklist:
                blacklist = []
            else:
                blacklist = [int(x) for x in blacklist.split(",")]
            config["BLACKLIST"] = blacklist
    else:
        whitelist = text(
            "What servers do you want to whitelist? Seperate each server ID with a comma.",
            validate=lambda x: (
                len(x) > 0
                and all(y.isnumeric() and 17 <= len(y) <= 19 for y in x.split(","))
            )
            or x == "",
            qmark="->",
        ).ask()
        if not whitelist:
            whitelist = []
        else:
            whitelist = [int(x) for x in whitelist.split(",")]
        config["WHITELIST"] = whitelist
    enable_channel_whitelist = select(
        "Do you want to enable channel whitelist? (This will only enter drops in the channels you specify)",
        choices=["yes", "no"],
        qmark="->",
    ).ask()
    config["CHANNEL_WHITELIST_ON"] = enable_channel_whitelist == "yes"
    if not config["CHANNEL_WHITELIST_ON"]:
        enable_blacklist = select(
            "Do you want to enable channel blacklist? (This will ignore drops in the channels you specify)",
            choices=["yes", "no"],
            qmark="->",
        ).ask()
        config["CHANNEL_BLACKLIST_ON"] = enable_blacklist == "yes"
        if config["CHANNEL_BLACKLIST_ON"]:
            blacklist = text(
                "What channels do you want to blacklist? Seperate each channel ID with a comma.",
                validate=lambda x: (
                    len(x) > 0
                    and all(y.isnumeric() and 17 <= len(y) <= 19 for y in x.split(","))
                )
                or x == "",
                qmark="->",
            ).ask()
            if not blacklist:
                blacklist = []
            else:
                blacklist = [int(x) for x in blacklist.split(",")]
            config["CHANNEL_BLACKLIST"] = blacklist
    else:
        whitelist = text(
            "What channels do you want to whitelist? Seperate each channel ID with a comma.",
            validate=lambda x: (
                len(x) > 0
                and all(y.isnumeric() and 17 <= len(y) <= 19 for y in x.split(","))
            )
            or x == "",
            qmark="->",
        ).ask()
        if not whitelist:
            whitelist = []
        else:
            whitelist = [int(x) for x in whitelist.split(",")]
        config["CHANNEL_WHITELIST"] = whitelist
    ignore_users = text(
        "What users do you want to ignore? Seperate each user ID with a comma.",
        validate=lambda x: (
            len(x) > 0
            and all(y.isnumeric() and 17 <= len(y) <= 19 for y in x.split(","))
        )
        or x == "",
        qmark="->",
    ).ask()
    if not ignore_users:
        ignore_users = []
    else:
        ignore_users = [int(x) for x in ignore_users.split(",")]
    config["IGNORE_USERS"] = ignore_users
    user_id = int(
        text(
            "What is your main accounts id?\n\nIf you are sniping from your main, put your main accounts' id.",
            validate=lambda x: x.isnumeric() and 17 <= len(x) <= 19,
            qmark="->",
        ).ask()
    )
    config["id"] = user_id
    channel_id = int(
        text(
            "What is the channel id where you want your alt to tip your main?\n(Remember, the tip.cc bot has to be in the server with this channel.)\n\nIf None, send 1.",
            validate=lambda x: x.isnumeric() and (17 <= len(x) <= 19 or int(x) == 1),
            default="1",
            qmark="->",
        ).ask()
    )
    config["channel_id"] = channel_id
    target_amount = float(
        text(
            "What is the target amount you want to tip your main at? Set it to 0 to disable.",
            validate=lambda x: validate_decimal(x),
            default="0",
            qmark="->",
        ).ask()
    )
    config["TARGET_AMOUNT"] = target_amount
    with open("config.json", "w") as f:
        dump(config, f, indent=4)
    logger.debug("Config saved.")


banned_words = set(config["BANNED_WORDS"])

client = Client(
    status=(
        Status.invisible
        if config["PRESENCE"] == "invisible"
        else (
            Status.online
            if config["PRESENCE"] == "online"
            else (
                Status.idle
                if config["PRESENCE"] == "idle"
                else Status.dnd if config["PRESENCE"] == "dnd" else Status.unknown
            )
        )
    )
)


@client.event
async def on_ready():
    global channel
    channel = client.get_channel(config["channel_id"])
    logger.info(f"Logged in as {client.user.name}#{client.user.discriminator}")
    if config["channel_id"] != 1 and client.user.id != config["id"]:
        tipping.start()
        logger.info("Tipping started.")
    else:
        logger.warning("Disabling tipping as requested.")


@tasks.loop(minutes=10.0)
async def tipping():
    await channel.send("$bals top")
    logger.debug("Sent command: $bals top")
    answer = await client.wait_for(
        "message",
        check=lambda message: message.author.id == 617037497574359050
        and message.embeds,
    )
    try:
        total_money = float(
            answer.embeds[0]
            .fields[-1]
            .value.split("$")[1]
            .replace(",", "")
            .replace("**", "")
            .replace(")", "")
            .replace("\u200b", "")
            .strip()
        )
    except Exception as e:
        logger.exception("Error occurred while getting total money, skipping tipping.")
        total_money = 0.0
    logger.debug(f"Total money: {total_money}")
    if total_money < config["TARGET_AMOUNT"]:
        logger.info("Target amount not reached, skipping tipping.")
        return
    try:
        pages = int(answer.embeds[0].author.name.split("/")[1].replace(")", ""))
    except:
        pages = 1
    if not answer.components:
        button_disabled = True
    for _ in range(pages):
        try:
            button = answer.components[0].children[1]
            button_disabled = button.disabled
        except:
            button_disabled = True
        for crypto in answer.embeds[0].fields:
            if "Estimated total" in crypto.name:
                continue
            if "DexKit" in crypto.name:
                content = f"$tip <@{config['id']}> all {crypto.name.replace('*', '').replace('DexKit (BSC)', 'bKIT')}"
            else:
                content = f"$tip <@{config['id']}> all {crypto.name.replace('*', '')}"
            async with channel.typing():
                await sleep(len(content) / randint(config["CPM"][0], config["CPM"][1]) * 60)
            await channel.send(content)
            logger.debug(f"Sent tip: {content}")
        if button_disabled:
            try:
                await answer.components[0].children[2].click()
                logger.debug("Clicked next page button")
                return
            except IndexError:
                try:
                    await answer.components[0].children[0].click()
                    logger.debug("Clicked first page button")
                    return
                except IndexError:
                    return
        else:
            await button.click()
            await sleep(1)
            answer = await channel.fetch_message(answer.id)


@tipping.before_loop
async def before_tipping():
    logger.info("Waiting for bot to be ready before tipping starts...")
    await client.wait_until_ready()


@client.event
async def on_message(original_message: Message):
    if (
        original_message.content.startswith(
            ("$airdrop", "$triviadrop", "$mathdrop", "$phrasedrop", "$redpacket")
        )
        and not any(word in original_message.content.lower() for word in banned_words)
        and (
            not config["WHITELIST_ON"]
            or (
                config["WHITELIST_ON"]
                and original_message.guild.id in config["WHITELIST"]
            )
        )
        and (
            not config["BLACKLIST_ON"]
            or (
                config["BLACKLIST_ON"]
                and original_message.guild.id not in config["BLACKLIST"]
            )
        )
        and (
            not config["CHANNEL_WHITELIST_ON"]
            or (
                config["CHANNEL_WHITELIST_ON"]
                and original_message.channel.id in config["CHANNEL_WHITELIST"]
            )
        )
        and (
            not config["CHANNEL_BLACKLIST_ON"]
            or (
                config["CHANNEL_BLACKLIST_ON"]
                and original_message.channel.id not in config["CHANNEL_BLACKLIST"]
            )
        )
        and original_message.author.id not in config["IGNORE_USERS"]
    ):
        logger.debug(
            f"Detected drop in {original_message.channel.name}: {original_message.content}"
        )
        try:
            tip_cc_message = await client.wait_for(
                "message",
                check=lambda message: message.author.id == 617037497574359050
                and message.channel.id == original_message.channel.id
                and message.embeds
                and message.embeds[0].footer
                and (
                    "ends" in message.embeds[0].footer.text.lower()
                    or (
                        "Trivia time - " in message.embeds[0].title
                        and "ended" in message.embeds[0].footer.text.lower()
                    )
                )
                and str(original_message.author.id) in message.embeds[0].description,
                timeout=15,
            )
            logger.debug("Detected tip.cc message from drop.")
        except TimeoutError:
            logger.exception(
                "Timeout occurred while waiting for tip.cc message, skipping."
            )
            return
        embed = tip_cc_message.embeds[0]
        if "$" not in embed.description or "≈" not in embed.description:
            money = 0.0
        else:
            try:
                money = float(
                    embed.description.split("≈")[1]
                    .split(")")[0]
                    .strip()
                    .replace("$", "")
                    .replace(",", "")
                )
            except IndexError:
                logger.exception(
                    "Index error occurred during money splitting, skipping..."
                )
                return
        if money < config["IGNORE_DROPS_UNDER"]:
            logger.info(
                f"Ignored drop for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}"
            )
            return
        for threshold in config["IGNORE_THRESHOLDS"]:
            logger.debug(
                f"Checking threshold: {threshold['threshold']} with chance: {threshold['chance']}"
            )
            if money <= threshold["threshold"]:
                logger.debug(
                    f"Drop value {money} is less than or equal to threshold {threshold['threshold']}"
                )
                random_number = randint(0, 100)
                if random_number < threshold["chance"]:
                    logger.info(
                        f"Ignored drop from failed threshold for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}"
                    )
                    return
        logger.debug(f"Money: {money}")
        logger.debug(f"Drop ends in: {embed.timestamp.timestamp() - time()}")
        drop_ends_in = embed.timestamp.timestamp() - time()
        if drop_ends_in < config["IGNORE_TIME_UNDER"]:
            logger.info(
                f"Ignored drop for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}"
            )
            return
        if (
            "An airdrop appears" in embed.title
            and config["DELAY_AIRDROP"]
            or "Trivia time - " in embed.title
            and config["DELAY_TRIVIADROP"]
            or "Math" in embed.title
            and config["DELAY_MATHDROP"]
            or "Phrase drop!" in embed.title
            and config["DELAY_PHRASEDROP"]
            or "appeared" in embed.title
            and config["DELAY_REDPACKET"]
        ):
            if config["SMART_DELAY"]:
                logger.debug("Smart delay enabled, waiting...")
                if drop_ends_in < 0:
                    logger.debug("Drop ended, skipping...")
                    return
                delay = drop_ends_in / 4
                logger.debug(f"Delay: {round(delay, 2)}")
                await sleep(delay)
                logger.info(f"Waited {round(delay, 2)} seconds before proceeding.")
            elif config["RANGE_DELAY"]:
                logger.debug("Range delay enabled, waiting...")
                delay = uniform(config["DELAY"][0], config["DELAY"][1])
                logger.debug(f"Delay: {delay}")
                await sleep(delay)
                logger.info(f"Waited {delay} seconds before proceeding.")
            elif config["DELAY"] != [0, 0]:
                logger.debug(f"Manual delay enabled, waiting {config['DELAY'][0]}...")
                await sleep(config["DELAY"][0])
                logger.info(f"Waited {config['DELAY'][0]} seconds before proceeding.")
        try:
            if "ended" in embed.footer.text.lower():
                logger.debug("Drop ended, skipping...")
                return
            elif "An airdrop appears" in embed.title and not config["DISABLE_AIRDROP"]:
                logger.debug("Airdrop detected, entering...")
                try:
                    button = tip_cc_message.components[0].children[0]
                except IndexError:
                    logger.exception(
                        "Index error occurred, meaning the drop most likely ended, skipping..."
                    )
                    return
                if "Enter airdrop" in button.label:
                    await button.click()
                    logger.info(
                        f"Entered airdrop in {original_message.channel.name} for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}"
                    )
                    if config["SEND_MESSAGE"]:
                        message = config["MESSAGES"][
                            randint(0, len(config["MESSAGES"]) - 1)
                        ]
                        length = len(message) / randint(config["CPM"][0], config["CPM"][1]) * 60
                        async with original_message.channel.typing():
                            await sleep(length)
                        await original_message.channel.send(message)
                        logger.info(f"Sent message: {message}")
                    return
            elif "Phrase drop!" in embed.title and not config["DISABLE_PHRASEDROP"]:
                logger.debug("Phrasedrop detected, entering...")
                content = embed.description.replace("\n", "").replace("**", "")
                content = content.split("*")
                try:
                    content = content[1].replace("​", "").replace("\u200b", "").strip()
                except IndexError:
                    logger.exception("Index error occurred, skipping...")
                    pass
                else:
                    logger.debug("Typing and sending message...")
                    length = len(content) / randint(config["CPM"][0], config["CPM"][1]) * 60
                    async with original_message.channel.typing():
                        await sleep(length)
                    await original_message.channel.send(content)
                    logger.info(
                        f"Entered phrasedrop in {original_message.channel.name} for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}"
                    )
                    if config["SEND_MESSAGE"]:
                        message = config["MESSAGES"][
                            randint(0, len(config["MESSAGES"]) - 1)
                        ]
                        length = len(message) / randint(config["CPM"][0], config["CPM"][1]) * 60
                        async with original_message.channel.typing():
                            await sleep(length)
                        await original_message.channel.send(message)
                        logger.info(f"Sent message: {message}")
                    return
            elif "appeared" in embed.title and not config["DISABLE_REDPACKET"]:
                logger.debug("Redpacket detected, claiming...")
                try:
                    button = tip_cc_message.components[0].children[0]
                except IndexError:
                    logger.exception(
                        "Index error occurred, meaning the drop most likely ended, skipping..."
                    )
                    return
                if "envelope" in button.label:
                    await button.click()
                    logger.info(
                        f"Claimed envelope in {original_message.channel.name} for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}"
                    )
                    if config["SEND_MESSAGE"]:
                        message = config["MESSAGES"][
                            randint(0, len(config["MESSAGES"]) - 1)
                        ]
                        length = len(message) / randint(config["CPM"][0], config["CPM"][1]) * 60
                        async with original_message.channel.typing():
                            await sleep(length)
                        await original_message.channel.send(message)
                        logger.info(f"Sent message: {message}")
                    return
            elif "Math" in embed.title and not config["DISABLE_MATHDROP"]:
                logger.debug("Mathdrop detected, entering...")
                content = embed.description.replace("\n", "").replace("**", "")
                content = content.split("`")
                try:
                    content = content[1].replace("​", "").replace("\u200b", "")
                except IndexError:
                    logger.exception("Index error occurred, skipping...")
                    pass
                else:
                    logger.debug("Evaluating math and sending message...")
                    answer = eval(content)
                    if isinstance(answer, float) and answer.is_integer():
                        answer = int(answer)
                    logger.debug(f"Answer: {answer}")
                    if not config["SMART_DELAY"] and config["DELAY"] == 0:
                        length = len(str(answer)) / randint(config["CPM"][0], config["CPM"][1]) * 60
                        async with original_message.channel.typing():
                            await sleep(length)
                    await original_message.channel.send(answer)
                    logger.info(
                        f"Entered mathdrop in {original_message.channel.name} for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}"
                    )
                    if config["SEND_MESSAGE"]:
                        message = config["MESSAGES"][
                            randint(0, len(config["MESSAGES"]) - 1)
                        ]
                        length = len(message) / randint(config["CPM"][0], config["CPM"][1]) * 60
                        async with original_message.channel.typing():
                            await sleep(length)
                        await original_message.channel.send(message)
                        logger.info(f"Sent message: {message}")
                    return
            elif "Trivia time - " in embed.title and not config["DISABLE_TRIVIADROP"]:
                logger.debug("Triviadrop detected, entering...")
                category = embed.title.split("Trivia time - ")[1].strip()
                bot_question = embed.description.replace("**", "").split("*")[1]
                async with ClientSession() as session:
                    async with session.get(
                        f"https://raw.githubusercontent.com/QuartzWarrior/OTDB-Source/main/{quote(category)}.csv"
                    ) as resp:
                        lines = (await resp.text()).splitlines()
                        for line in lines:
                            question, answer = line.split(",")
                            if bot_question.strip() == unquote(question).strip():
                                answer = unquote(answer).strip()
                                try:
                                    buttons = tip_cc_message.components[0].children
                                except IndexError:
                                    logger.exception(
                                        "Index error occurred, meaning the drop most likely ended, skipping..."
                                    )
                                    return
                                for button in buttons:
                                    if button.label.strip() == answer:
                                        await button.click()
                                logger.info(
                                    f"Entered triviadrop in {original_message.channel.name} for {embed.description.split('**')[1]} {embed.description.split('**')[2].split(')')[0].replace(' (','')}"
                                )
                                if config["SEND_MESSAGE"]:
                                    message = config["MESSAGES"][
                                        randint(0, len(config["MESSAGES"]) - 1)
                                    ]
                                    length = len(message) / randint(config["CPM"][0], config["CPM"][1]) * 60
                                    async with original_message.channel.typing():
                                        await sleep(length)
                                    await original_message.channel.send(message)
                                    logger.info(f"Sent message: {message}")
                                return

        except AttributeError:
            logger.exception("Attribute error occurred")
            return
        except HTTPException:
            logger.exception("HTTP exception occurred")
            return
        except NotFound:
            logger.exception("Not found exception occurred")
            return
    elif original_message.content.startswith(
        ("$airdrop", "$triviadrop", "$mathdrop", "$phrasedrop", "$redpacket")
    ) and any(word in original_message.content.lower() for word in banned_words):
        logger.info(
            f"Banned word detected in {original_message.channel.name}, skipping..."
        )
    elif original_message.content.startswith(
        ("$airdrop", "$triviadrop", "$mathdrop", "$phrasedrop", "$redpacket")
    ) and (
        config["WHITELIST_ON"] and original_message.guild.id not in config["WHITELIST"]
    ):
        logger.info(
            f"Whitelist enabled and drop not in whitelist, skipping {original_message.channel.name}..."
        )
    elif original_message.content.startswith(
        ("$airdrop", "$triviadrop", "$mathdrop", "$phrasedrop", "$redpacket")
    ) and (config["BLACKLIST_ON"] and original_message.guild.id in config["BLACKLIST"]):
        logger.info(
            f"Blacklist enabled and drop in blacklist, skipping {original_message.channel.name}..."
        )
    elif original_message.content.startswith(
        ("$airdrop", "$triviadrop", "$mathdrop", "$phrasedrop", "$redpacket")
    ) and (
        config["CHANNEL_BLACKLIST_ON"]
        and original_message.channel.id in config["CHANNEL_BLACKLIST"]
    ):
        logger.info(
            f"Channel blacklist enabled and drop in channel blacklist, skipping {original_message.channel.name}..."
        )
    elif (
        original_message.content.startswith(
            ("$airdrop", "$triviadrop", "$mathdrop", "$phrasedrop", "$redpacket")
        )
        and original_message.author.id in config["IGNORE_USERS"]
    ):
        logger.info(
            f"User in ignore list detected in {original_message.channel.name}, skipping..."
        )


if __name__ == "__main__":
    try:
        client.run(config["TOKEN"])

    except LoginFailure:
        logger.critical("Invalid token, restart the program.")
        config["TOKEN"] = ""
        with open("config.json", "w") as f:
            dump(config, f, indent=4)
