

import os
import re
import platform
import subprocess
import unittest
import time
import logging
import shlex
import queue
import SublimeGtags.gtags_project
import threading

from SublimeGtags.gtags_project import GtagsProject

logging.basicConfig(format="[%(asctime)s] - [%(name)s] - [%(levelname)s] - \n%(message)s\n")
logger = logging.getLogger('Symbol')
logger.setLevel(logging.DEBUG)

BIN_PATH=os.path.dirname(os.path.abspath(__file__)) +"/bin/"+ platform.system()
SYMBOL_PATTERN = '(?P<symbol>[^\s]+)\s+(?P<line>[^\s]+)\s+(?P<path>[^\s]+)\s+(?P<signature>.*)'
SYMBOL_RE = re.compile(SYMBOL_PATTERN)

class GtagsSymbol(object):

	kwargs=None
	gtags_root=""
	gtags_lib_path=""
	pwd=None
	file_changed_queue=queue.Queue(50)
	auto_update_thread=None
	build_tags_thread=None
	def __init__(self, file_path=None):

		GtagsSymbol.pwd = GtagsProject().get_pwd(file_path)
		self.setup_kwargs()
		if GtagsSymbol.auto_update_thread is None:
			logger.info("creat auto update thread")
			GtagsSymbol.auto_update_thread = threading.Thread(target=self.auto_update)
			GtagsSymbol.auto_update_thread.start()

		if GtagsSymbol.gtags_root is None or GtagsProject().is_changed():

			# get the gtags root (GTAGSROOT) which contains the GTAGS files
			config         = GtagsProject().get_config()
			logger.info("config: %s", config)
			gtags_root     = config.get('GTAGSROOT')
			gtags_lib_path = config.get('GTAGSLIBPATH')

			if gtags_lib_path is not None:
				GtagsSymbol.gtags_lib_path = gtags_lib_path

			if gtags_root is not None:
				GtagsSymbol.gtags_root = os.path.normpath(gtags_root)
				self.setup_kwargs()
				logger.info("update gtags root: %s", GtagsSymbol.gtags_root)
			else:
				self.setup_kwargs()
				logger.warning("the gtags_root is None!")

			# get the additional library tag files if we have

			#	GtagsSymbol.gtags_lib_path = os.pathsep.join(gtags_lib_path)

		logger.info("Symbol init, root: %s, lib: %s", GtagsSymbol.gtags_root, GtagsSymbol.gtags_lib_path)

	def setup_kwargs(self):
		# setup environment variable
		exec_env = {}
		exec_env['PATH'] = os.environ['PATH']
		exec_env['PATH'] = os.path.normpath(BIN_PATH)
		exec_env['GTAGSROOT'] = GtagsSymbol.pwd

		if GtagsSymbol.gtags_lib_path is not None:
			exec_env['GTAGSLIBPATH'] = os.pathsep.join(GtagsSymbol.gtags_lib_path)


		# setup the parameters for the subprocess interface
		GtagsSymbol.kwargs={}
		# shell=True will add "cmd /c" before "global -x", to avoid popup window
		if platform.system() == "Windows":
			GtagsSymbol.kwargs.update(shell=True)

		# set the environment variable
		GtagsSymbol.kwargs.update(env=exec_env)
		# we will need the result of the global command
		GtagsSymbol.kwargs.update(stdout=subprocess.PIPE)
		GtagsSymbol.kwargs.update(stderr=subprocess.PIPE)
		# set the current working directory to the gtags root dir
		GtagsSymbol.kwargs.update(cwd=GtagsSymbol.pwd)
		# the stdout will be sting lines instead of bytes when universal_newlines is True
		GtagsSymbol.kwargs.update(universal_newlines=True)


		logger.info("setup kwargs: %s", GtagsSymbol.kwargs)

	# this function is used to exec the global command line
	def exec_cmd(self, cmd):

		if GtagsSymbol.gtags_root is None:
			logger.warning("the gtags_root is None!")
			#return None

		logger.debug("time before run command: %s", time.time())
		logger.info("run command: %s, kwargs: %s", cmd, GtagsSymbol.kwargs)

		args = shlex.split(cmd)
		return subprocess.Popen(args, **GtagsSymbol.kwargs)

	def update(self, file_path):
		# Update tag file incrementally
		#h = self.exec_cmd("gtags --single-update " + file_path)
		h = self.exec_cmd("global -u")
		if h is None:
			logger.warning("can not exec gtags!")
			return -1
		return 0

	def version(self, file_path):
		h = self.exec_cmd("global --version")
		if h is None:
			logger.warning("can not exec global!")
			return -1
		stdout, stderr = h.communicate()
		if len(stderr) > 0:
			logger.error(stderr)

		logger.info(stdout)

		h = self.exec_cmd("gtags --version")
		if h is None:
			logger.warning("can not exec gtags!")
			return -1
		stdout, stderr = h.communicate()
		if len(stderr) > 0:
			logger.error(stderr)

		logger.info(stdout)

		return 0

	def sfupdate(self, file_path):

		file_type = os.path.splitext(file_path)[1]
		logger.info("sfupdate file type %s", file_type)

		if ".h" in file_type:
			ret = 0
		elif ".c" in file_type:
			ret = 0
		elif ".cpp" in file_type:
			ret = 0
		elif ".java" in file_type:
			ret = 0
		else:
			logger.error("file type %s not supported", file_type)
			return -1

		ret = GtagsProject().is_file_in_project(file_path)
		if ret is False:
			return -2

		# Update tag file incrementally
		h = self.exec_cmd("gtags --single-update " + file_path)
		#h = self.exec_cmd("global -u")
		if h is None:
			logger.warning("can not exec gtags!")
			return -1
		h.wait()
		logger.info("sfupdate done!")
		return 0

	def auto_update(self):
		logger.info("auto_update start!")
		while True:
			try:
				file_path = GtagsSymbol.file_changed_queue.get()
				self.sfupdate(file_path)
			except queue.Empty:
				time.sleep(2)
				pass

	def file_changed(self, file_path):
		ret = GtagsProject().is_file_in_project(file_path)
		if ret is False:
			return -2

		logger.info("queue put: %s!", file_path)
		GtagsSymbol.file_changed_queue.put(file_path)
		return 0

	def search(self, options, arg):

		if options is None or arg is None:
			logger.error("the options(%s) or arg(%s) error", options, arg)
			return []

		h = self.exec_cmd("global " + options + " " + arg)
		#h = self.exec_cmd("global " + options) # test errors msg output
		if h is None:
			logger.warning("can not exec global!")
			return []

		# read the stdout and stderr
		stdout, stderr = h.communicate()

		if len(stderr) > 0:
			logger.error(stderr)

		lines = stdout.splitlines()
		logger.debug("time after run command global: %s, lines: %s", time.time(), lines)


		matches = []
		if options == "-ax" or options == "-axr" or options == "-axf":
			# format the definitions or references
			for line in lines:
				matches.append(SYMBOL_RE.search(line).groupdict())

		elif options == "-axc":
			# format the completions
			matches = [ (line + "\tGtags", line) for line in lines ]
			#matches = [ (line, line) for line in lines ]

		else:
			logger.error("unsported options %s!", options)

		logger.debug("time after format the results: %s ", time.time())
		logger.info("got %d results", len(matches))
		return matches


	# Description
	# 		get the definitions of the symbol
	# Peremeters
	# 		name[in], the symbol which we want to search its definitions
	# return
	#		it will return [] if we cann't find definitions in the gtags.
	#       and if we got the definitions, it will return the definitions
	#       formated as below:
	#       [
	#           {
	#                "symbol": "name",
	#                "line": "567",
	#                "path": "/tmp/test.c",
	#                "signature": "struct name {;"
	#           }
	#           { ... } // more definitions
	#       ]
	def get_definitions(self, name):

		logger.info("get the definitions of symbol")
		"""
		test = [ {"symbol": "name1", "line": "51", "path": "/tmp/test1.c", "signature": "struct name1 {;"},
		         {"symbol": "name2", "line": "52", "path": "/tmp/test2.c", "signature": "struct name2 {;"},
		       ]
		return test
		"""
		return self.search("-ax", name)


	# Description
	# 		get the references of the symbol
	# Peremeters
	# 		name[in], the symbol which we want to search its references
	# return
	#		it will return [] if we cann't find references in the gtags.
	#       and if we got the references, it will return the references
	#       formated as below:
	#       [
	#           {
	#                "symbol": "name",
	#                "line": "567",
	#                "path": "/tmp/test.c",
	#                "signature": "struct name {;"
	#           }
	#           { ... }
	#           ... # more references
	#       ]
	def get_references(self, name):

		logger.info("get the references of symbol")

		return self.search("-axr", name)


	# Description
	# 		get the completions of specific prefix
	# Peremeters
	# 		prefix[in], the prefix to search the completions
	# return
	#		it will return [] if we cann't find references in the gtags.
	#       and if we got the references, it will return the references
	#       formated as below:
	#       [
	#           ("complt1\tGtags", "complt1"),
	#           ("complt2\tGtags", "complt2"),
	#           ... # more completions
	#       ]
	def get_completions(self, prefix):

		logger.info("get the completions")

		return self.search("-axc", prefix)


	# Description
	# 		get the definitions in the specific file
	# Peremeters
	# 		file_path[in], the file to search the definitions
	# return
	#		it will return [] if we cann't find definitions in the file.
	#       and if we got the definitions, it will return the definitions
	#       formated as below:
	#       [
	#           {
	#                "symbol": "name",
	#                "line": "567",
	#                "path": "/tmp/test.c",
	#                "signature": "struct name {;"
	#           }
	#           { ... }
	#           ... # more references
	#       ]
	def get_all_symbol_definitions_of_file(self, file_path):

		logger.info("get the symbol definitions in the file")

		#return self.search("-axf", file_path)
		#return self.search("-axf", "D:/SourceCode/U3/u3_sys/linux/drivers/usb/gadget/m66592-udc.c")
		if platform.system() == "Windows":
			file_path = file_path.replace("\\", "/")
		return self.search("-axf", file_path)

	def build_tags(self):

		if GtagsSymbol.build_tags_thread is None:
			logger.info("creat build_tags thread")
			GtagsSymbol.build_tags_thread = threading.Thread(target=self.thread_build_tags)
			GtagsSymbol.build_tags_thread.start()
			building_tags = threading.Thread(target=self.building_tags)
			building_tags.start()

	def thread_build_tags(self):

		logger.info("thread_build_tags begin")
		self.setup_kwargs()
		h = self.exec_cmd("gtags --sqlite3")
		#h = self.exec_cmd("global " + options) # test errors msg output
		if h is None:
			logger.warning("can not exec global!")
			logger.debug("thread_build_tags failed!")
			GtagsSymbol.build_tags_thread = None
			return -1

		# read the stdout and stderr
		stdout, stderr = h.communicate()

		if len(stderr) > 0:
			logger.error(stderr)
			logger.debug("thread_build_tags failed!")
			GtagsSymbol.build_tags_thread = None
			return -1

		logger.debug("thread_build_tags successfully!")
		logger.debug(stdout)
		GtagsSymbol.build_tags_thread = None

		return 0

	def building_tags(self):

		counter = 0;
		while GtagsSymbol.build_tags_thread is not None:
			counter = counter + 1
			logger.info("building tags [%d]", counter)
			time.sleep(1)
			pass
		return 0

class SymbolTest(unittest.TestCase):

	def test_start_with(self):
		print("test_start_with")
		print("==============================================\n\n\n")


if __name__ == '__main__':
	unittest.main()
