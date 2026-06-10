from datetime import timedelta
import logging
from logging.handlers import RotatingFileHandler
from telegram.ext import Application


from callback import Jobs
from const.CONFIG import CONFIG
from handlers import Handlers

logging.basicConfig(handlers=[RotatingFileHandler("./logs.log", maxBytes=10000, backupCount=4)],
                    level=logging.INFO,
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
                    datefmt="%Y-%m-%dT%H:%M:%S", )

logger = logging.getLogger(__name__)

aps_logger = logging.getLogger('apscheduler')
aps_logger.setLevel(logging.ERROR)


def main():
	application = Application.builder().token(CONFIG.BOTTOKEN).build()
	job_q = application.job_queue
	job_q.run_repeating(
		callback=Jobs.supervisor, interval=timedelta(minutes=5), first=5
		)
	job_q.run_once(callback=Jobs.set_commands, when=3)
	for handler in Handlers.get_group(0):
		application.add_handler(handler, group=0)
	for handler in Handlers.get_group(1):
		application.add_handler(handler, group=1)

	if CONFIG.PORT_NUM != 0:
		application.run_webhook(
			listen="127.0.0.1", port=CONFIG.PORT_NUM, url_path=CONFIG.BOTTOKEN
			)
	else:
		application.run_polling()



if __name__ == "__main__":
	main()
