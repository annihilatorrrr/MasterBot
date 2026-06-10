from telegram import Update
from telegram.ext import CommandHandler, TypeHandler, CallbackQueryHandler

from callback import Misc, Restart, Stats
	

class Handlers:
    block_access = TypeHandler(type=Update, callback=Misc.block_access)
    start = CommandHandler("start", Misc.start_command)
    logs = CommandHandler("logs", Misc.get_logs)
    logs_callback = CallbackQueryHandler(Misc.logs_callback, pattern="^logs_")
    restart = CommandHandler("restart", Restart.command)
    restart_callback = CallbackQueryHandler(Restart.command, pattern="^restart")
    get_all = CommandHandler("get", Misc.get_all)
    help_command = CommandHandler("help", Misc.help_command)
    stats = CommandHandler("stats", Stats.command)
    detail_stats = CommandHandler("detail_stats", Stats.detail_command)
    stats_refresh = CallbackQueryHandler(Stats.command, pattern="refresh")

    @staticmethod
    def get_group(group_number: int) -> list:
        if group_number == 0:
            return [Handlers.block_access]

        elif group_number == 1:
            return [Handlers.start, Handlers.logs, Handlers.logs_callback, Handlers.restart, Handlers.restart_callback, Handlers.get_all, Handlers.help_command, Handlers.stats, Handlers.detail_stats, Handlers.stats_refresh]
        else:
            return []
	