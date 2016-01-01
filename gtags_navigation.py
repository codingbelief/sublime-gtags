

import sublime
import sublime_plugin
import logging
import os
import math
logging.basicConfig(format="[%(asctime)s] - [%(name)s] - [%(levelname)s] - \n%(message)s\n")
logger = logging.getLogger('Navigation')
logger.setLevel(logging.DEBUG)


class GtagsNavigation(object):
	trace = [];
	current_index = 0;
	trace0 = [];
	current_index0 = 0;
	trace1 = [];
	current_index1 = 0;
	cursor_lock = 0;

	def lock(self):
		GtagsNavigation.cursor_lock = 1

	def unlock(self):
		GtagsNavigation.cursor_lock = 0

	def add(self, path, line, symbol=None):
		logger.info("GtagsNavigation add")
		GtagsNavigation.trace = GtagsNavigation.trace0
		GtagsNavigation.current_index = GtagsNavigation.current_index0
		self.__add(path, line, symbol)
		GtagsNavigation.trace0 = GtagsNavigation.trace
		GtagsNavigation.current_index0 = GtagsNavigation.current_index

	def show_trace(self):
		GtagsNavigation.trace = GtagsNavigation.trace0
		GtagsNavigation.current_index = GtagsNavigation.current_index0
		self.__show_trace()
		GtagsNavigation.trace0 = GtagsNavigation.trace
		GtagsNavigation.current_index0 = GtagsNavigation.current_index

	def forward(self):
		GtagsNavigation.cursor_lock = 1
		GtagsNavigation.trace = GtagsNavigation.trace0
		GtagsNavigation.current_index = GtagsNavigation.current_index0
		self.__forward()
		GtagsNavigation.trace0 = GtagsNavigation.trace
		GtagsNavigation.current_index0 = GtagsNavigation.current_index


	def backward(self):
		GtagsNavigation.cursor_lock = 1
		GtagsNavigation.trace = GtagsNavigation.trace0
		GtagsNavigation.current_index = GtagsNavigation.current_index0
		self.__backward()
		GtagsNavigation.trace0 = GtagsNavigation.trace
		GtagsNavigation.current_index0 = GtagsNavigation.current_index

	def set_cur_index(self, index):
		GtagsNavigation.trace = GtagsNavigation.trace0
		GtagsNavigation.current_index = GtagsNavigation.current_index0
		self.__set_cur_index(index)
		GtagsNavigation.trace0 = GtagsNavigation.trace
		GtagsNavigation.current_index0 = GtagsNavigation.current_index


	def add_cursor_trace(self, path, line, symbol=None):
		if GtagsNavigation.cursor_lock == 1:
			GtagsNavigation.cursor_lock = 0
			return

		if path is None:
			logger.info("GtagsNavigation add_cursor_trace, path is None")
			return

		logger.info("GtagsNavigation add_cursor_trace")
		GtagsNavigation.trace = GtagsNavigation.trace1
		GtagsNavigation.current_index = GtagsNavigation.current_index1
		self.__add(path, line, symbol)
		GtagsNavigation.trace1 = GtagsNavigation.trace
		GtagsNavigation.current_index1 = GtagsNavigation.current_index

	def show_cursor_trace(self):
		GtagsNavigation.trace = GtagsNavigation.trace1
		GtagsNavigation.current_index = GtagsNavigation.current_index1
		self.__show_trace()
		GtagsNavigation.trace1 = GtagsNavigation.trace
		GtagsNavigation.current_index1 = GtagsNavigation.current_index

	def forward_cursor_trace(self):
		GtagsNavigation.trace = GtagsNavigation.trace1
		GtagsNavigation.current_index = GtagsNavigation.current_index1
		self.__forward()
		GtagsNavigation.trace1 = GtagsNavigation.trace
		GtagsNavigation.current_index1 = GtagsNavigation.current_index

	def backward_cursor_trace(self):
		GtagsNavigation.trace = GtagsNavigation.trace1
		GtagsNavigation.current_index = GtagsNavigation.current_index1
		self.__backward()
		GtagsNavigation.trace1 = GtagsNavigation.trace
		GtagsNavigation.current_index1 = GtagsNavigation.current_index

	def set_cursor_trace_cur_index(self, index):
		GtagsNavigation.trace = GtagsNavigation.trace1
		GtagsNavigation.current_index = GtagsNavigation.current_index1
		self.__set_cur_index(index)
		GtagsNavigation.trace1 = GtagsNavigation.trace
		GtagsNavigation.current_index1 = GtagsNavigation.current_index

	def __add(self, path, line, symbol=None):
		# view = sublime.active_window().active_view()
		# symbol = view.substr(view.word(view.sel()[0].a))
		if len(GtagsNavigation.trace) == 0:
			index = 0;
			GtagsNavigation.current_index = 0
		else:
			index = GtagsNavigation.current_index + 1

			# we don't add if the new trace is close to the prev
			line_abs = math.fabs(int(line) - int(GtagsNavigation.trace[index-1].get('line')))
			#logger.info("line abs: %s", line_abs)
			if path == GtagsNavigation.trace[index-1].get('path') and \
			   line_abs < 3.0:
				logger.info("new trace is close to the prev, line abs: %s", line_abs)
				return

			# we don't add if the new trace is close to the next
			if index < len(GtagsNavigation.trace):
				line_abs = math.fabs(int(line) - int(GtagsNavigation.trace[index].get('line')))
				if path == GtagsNavigation.trace[index].get('path') and \
				   line_abs < 3.0:
					logger.info("new trace is close to the next, line abs: %s", line_abs)
					if index < len(GtagsNavigation.trace):
						GtagsNavigation.current_index = index
					return

		GtagsNavigation.current_index = index
		logger.info("add trace: %s:%s:%s", symbol, line, path)
		GtagsNavigation.trace.insert(index, {'path':path, 'line':line, 'symbol':symbol})

		if len(GtagsNavigation.trace) > 1000:
			GtagsNavigation.trace.pop(0)
			GtagsNavigation.current_index = GtagsNavigation.current_index - 1

		logger.info("trace len: %s, index: %s", len(GtagsNavigation.trace), GtagsNavigation.current_index)

	def __show_trace(self):

		return GtagsNavigation.trace

	def __forward(self):
		if GtagsNavigation.current_index >= len(GtagsNavigation.trace)-1:
			return

		if len(GtagsNavigation.trace) == 0:
			return;
		elif len(GtagsNavigation.trace) == 1:
			index = 0;
		else:
			index = GtagsNavigation.current_index+1;
			GtagsNavigation.current_index = index;

		path = GtagsNavigation.trace[index].get('path')
		line = GtagsNavigation.trace[index].get('line')
		logger.info("forward to file: %s:%s", line, path)

		position = '%s:%d:0' % (os.path.normpath(path), int(line))
		sublime.active_window().open_file(position, sublime.ENCODED_POSITION)

	def __backward(self):
		if GtagsNavigation.current_index == 0 and len(GtagsNavigation.trace) != 1:
			return

		if len(GtagsNavigation.trace) == 0:
			return;
		elif len(GtagsNavigation.trace) == 1:
			index = 0;
		else:
			index = GtagsNavigation.current_index-1;
			GtagsNavigation.current_index = index;

		path = GtagsNavigation.trace[index].get('path')
		line = GtagsNavigation.trace[index].get('line')
		logger.info("backward to file: %s:%s", line, path)

		position = '%s:%d:0' % (os.path.normpath(path), int(line))
		sublime.active_window().open_file(position, sublime.ENCODED_POSITION)

	def __set_cur_index(self, index):
		if index > 0 and index < len(GtagsNavigation.trace):
			GtagsNavigation.current_index=index
			logger.info("set index: %s", index)

	def __cleanup(self):
		GtagsNavigation.trace = [];
		GtagsNavigation.current_index = 0;


