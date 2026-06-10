import time
from telegram import Update, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import CallbackContext, ApplicationHandlerStop, filters as Filters

from common import get_list_of_py, get_recent_logs_for_alias
from const import CONFIG, KeyboardMK


class Misc:
    @staticmethod
    async def block_access(update: Update, context: CallbackContext):
        # ignore service messages/where there is no effective_message
        if update.effective_message is None or Filters.StatusUpdate.ALL.check_update(update):
            raise ApplicationHandlerStop
        if update.effective_user.id not in CONFIG.ADMINS:
            await update.effective_message.reply_html(
                """
Hello there, non-admin Human!
    I'm the MasterBot. I help admin in managing bots/programs in your server.

<b>What can I do?</b>
    1. Pull the latest update of a repo to server and restart appropriate bot
    2. Monitor the server statistics
    3. Notify about the failed/stopped bots
    4. Get recent logs of bots
    """,
                reply_markup=KeyboardMK.repo(),
            )
            raise ApplicationHandlerStop

    @staticmethod
    async def start_command(update: Update, context: CallbackContext):
        await update.effective_message.reply_html(
            """
Hello there, Admin!
    I'm the MasterBot. You already know what I do, hit /help for list of commands.
    """
        )

    @staticmethod
    async def help_command(update: Update, context: CallbackContext):
        await update.effective_message.reply_html(
            """
<b>HELP</b>
    
    1. /get - Returns all the py programs running on server
    2. /restart alias - Stops the program > Fetches the latest update from repo > Starts the program again
    3. /stats - Gets statistics of CPU/Memory usages
    4. /detail_stats - Gets detailed statistics of all processes
    5. /logs - Gets the latest logs of a specific bot
    """
        )

    @staticmethod
    async def get_all(update: Update, context: CallbackContext):
        to_send = """
<b>List of py processes running</b>
<code>cmd     filename    alias</code>

"""
        for p in get_list_of_py():
            to_send += "<code>" + " ".join(arg for arg in p.cmdline()) + "</code>\n"
        await update.effective_message.reply_html(to_send)

    @staticmethod
    async def get_logs(update: Update, context: CallbackContext):
        # build a inline kb with all the aliases of py processes, so that user can select which bot logs to get
        kb = []
        for p in get_list_of_py():
            alias = p.cmdline()[-1]
            kb.append([KeyboardMK.get_logs_btn(alias)])
        await update.effective_message.reply_html(
            "Select the bot to get logs from:", reply_markup=InlineKeyboardMarkup(kb)
        )
    
    @staticmethod
    async def logs_callback(update: Update, context: CallbackContext):
        await update.callback_query.answer("Fetching logs")
        alias = update.callback_query.data.split("_", maxsplit=1)[-1]
        logs_line_count = 200
        sent = False
        retries = 3
        while not sent and retries > 0:
            result = get_recent_logs_for_alias(alias, line_count=logs_line_count)
            if result is None:
                await update.effective_message.reply_html(
                    f"Couldn't find a running process/log file for alias <b>{alias}</b>. It might have stopped or doesn't have permission to access the log file.",
                )
                return
            

            _, logs = result
            fetched_on = f"<tg-time unix=\"{int(time.time())}\" format=\"r\">{update.callback_query.message.date.strftime('%Y-%m-%d %H:%M:%S')}</tg-time>"
            try:
                await update.effective_message.reply_html(
                    f"<b>Logs of {alias}</b> (recent {logs_line_count} lines)\n<blockquote expandable>{logs}</blockquote>\nFetched {fetched_on}",
                    reply_markup=InlineKeyboardMarkup([[KeyboardMK.get_logs_btn(alias, f"🔁 Refresh")]]),  # add a refresh button for the same alias
                )
                sent = True
            except BadRequest as e:
                if "Message is too long" in str(e):
                    logs_line_count //= 2
                else:
                    raise
            retries -= 1