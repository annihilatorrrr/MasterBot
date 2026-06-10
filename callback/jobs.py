import asyncio
from html import escape
import logging

from telegram import BotCommand, BotCommandScopeAllPrivateChats
from telegram.ext import CallbackContext
from telegram.error import BadRequest, Forbidden

from common import get_list_of_py
from const import CONFIG

logger = logging.getLogger(__name__)


class Jobs:
    @staticmethod
    async def supervisor(context: CallbackContext):
        if "prev_bot_list" not in context.bot_data:
            # load list of running bots for the first time
            context.bot_data["prev_bot_list"] = {
                bot for bot in get_list_of_py(only_alias=True)
            }
            context.bot_data["current_bot_list"] = {
                bot for bot in get_list_of_py(only_alias=True)
            }
        else:
            # shift the "current" to "prev" and fetch "new" as "current"
            context.bot_data["prev_bot_list"] = context.bot_data["current_bot_list"]
            context.bot_data["current_bot_list"] = {
                bot for bot in get_list_of_py(only_alias=True)
            }

            failed_bots = (
                context.bot_data["prev_bot_list"] - context.bot_data["current_bot_list"]
            )
            if failed_bots:
                failed_bots_list = "\n\t".join(escape(bot) for bot in failed_bots)
                to_send = (
                    f"<b>Attention, Master!</b>"
                    f"\nSome bots aren't running now and have escaped my hold, (compared to my previous list)"
                    f"\n"
                    f"\n<code>Alias</code>"
                    f"\n"
                    f"\n\t{failed_bots_list}"
                    f"\n"
                    f"\nI don't have the permission to start bots, please login to the VPS at your convenience"
                )
                for admin in CONFIG.ADMINS:
                    try:
                        await context.bot.send_message(chat_id=admin, text=to_send, parse_mode="HTML")
                    except (Forbidden, BadRequest): pass
                    except Exception as e:
                        logger.exception(f"{e}")

    @staticmethod
    async def set_commands( context: CallbackContext ):
        commands = [BotCommand("start", "start the bot"),
			BotCommand("restart", "restart a bot/script using alias"),
			BotCommand("logs", "get logs of a bot/script"),
			BotCommand("get", "get all running py processes"),
			BotCommand("stats", "stats of the server"),
			BotCommand("detail_stats", "stats of the processes"),
			BotCommand("help", "help message")]
        # for command in commands:
        retries = 5
        while retries > 0:
            try:
                await context.bot.set_my_commands(
                    commands,
                    language_code="en",
                    scope=BotCommandScopeAllPrivateChats()
                    )
            except Exception as e:
                retries -= 1
                await asyncio.sleep(3 * retries)
                if retries < 0:
                    raise e
                else:
                    break
            else:
                break