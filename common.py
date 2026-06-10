from datetime import datetime
import subprocess
from typing import Iterator
from collections import deque

from humanize import naturaldelta
import psutil
from psutil import Process
import os
import signal


def convert_to_GB( input_bytes ):
	return round(input_bytes / (1024 * 1024 * 1024), 1)


def kill_proc_tree(
		pid, sig=signal.SIGTERM, include_parent=True, timeout=None, on_terminate=None
		):
	"""Kill a process tree (including grandchildren) with signal
    "sig" and return a (gone, still_alive) tuple.
    "on_terminate", if specified, is a callback function which is
    called as soon as a child terminates.
    """
	if pid == os.getpid():
		raise RuntimeError("I refuse to kill myself")
	parent = psutil.Process(pid)
	children = parent.children(recursive=True)
	if include_parent:
		children.append(parent)
	for p in children:
		p.send_signal(sig)
	gone, alive = psutil.wait_procs(children, timeout=timeout, callback=on_terminate)
	return (gone, alive)


def get_list_of_py( only_alias=False ) -> Iterator[psutil.Process | str]:
	process_list = psutil.process_iter()
	for p in process_list:
		try:
			name = p.name()
		except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
			continue

		if name.startswith("python") or name.startswith("telegram-bot-api"):
			if only_alias:
				try:
					yield p.cmdline()[-1]
				except (IndexError, psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
					continue
			else:
				try:
					# Touch process metadata to skip stale/zombie/inaccessible entries.
					p.cmdline()
				except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
					continue
				yield p


def get_full_info( given_alias: str ) -> Process:
	for process in get_list_of_py():
		try:
			if given_alias == process.cmdline()[-1]:  # assume alias is the last arg
				return process
		except (IndexError, psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
			continue


def get_latest_log_file( process: Process ) -> str | None:
	"""Return the most recently modified .log file for the process, or nohup.out fallback."""
	candidate_logs: list[tuple[float, str]] = []
	try:
		for f in process.open_files():
			if f.path.endswith(".log"):
				try:
					candidate_logs.append((os.path.getmtime(f.path), f.path))
				except OSError:
					continue
	except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
		return None

	if candidate_logs:
		return max(candidate_logs, key=lambda item: item[0])[1]

	try:
		fallback_nohup = os.path.join(process.cwd(), "nohup.out")
		if os.path.isfile(fallback_nohup):
			return fallback_nohup
	except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied, OSError):
		return None

	return None


def read_last_lines( file_path: str, line_count: int = 200 ) -> str:
	with open(file_path, "r", encoding="utf-8", errors="replace") as f:
		return "".join(deque(f, maxlen=line_count))


def get_recent_logs_for_alias( alias: str, line_count: int = 200 ) -> tuple[str, str] | None:
	process = get_full_info(alias)
	if process is None:
		return None

	log_file = get_latest_log_file(process)
	if log_file is None:
		return None

	return log_file, read_last_lines(log_file, line_count)


def start_program( path, arg ):
	"""
    Activates the virtualenv 'env' inside path and executes the arg

    :param path: path of the program's dir
    :param arg:
    :return:
    """
	cmd = f"source env/bin/activate; nohup {arg} &"
	subprocess.Popen(cmd, shell=True, cwd=path, executable="/bin/bash")


def str_uptime( secs: float ):
	return naturaldelta(secs)


def update_repo( path ):
	"""
    Fetches the latest update of the repo located at path

    :param path:
    :return:
    """
	cmd = "git pull"
	try:
		return {"exit-code": 0,
		        "output": subprocess.check_output(
			        cmd, shell=True, cwd=path,
			        executable="/bin/bash", universal_newlines=True)
		        }
	except subprocess.CalledProcessError as e:
		return {"exit-code": e.returncode, "output": e.stderr}
