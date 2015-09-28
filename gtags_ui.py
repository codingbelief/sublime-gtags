import sublime
import sublime_plugin
import SublimeGtags.gtags_event
import SublimeGtags.gtags_navigation
import logging
from SublimeGtags.gtags_event import GtagsEventListener
from SublimeGtags.gtags_navigation import GtagsNavigation
import os
from sublime_plugin import all_callbacks

logging.basicConfig(format="[%(asctime)s] - [%(name)s] - [%(levelname)s] - \n%(message)s\n")
logger = logging.getLogger('UI')
logger.setLevel(logging.DEBUG)


class GtagsUIQuickPanel(object):
	symbol = None
	show_traces = False
	def file_jump(self, path, line=None):
		if path is not None:
			logger.info("jump to file: %s:%s", line, path)
			position = '%s:%d:0' % (os.path.normpath(path), int(line))
			sublime.active_window().open_file(position, sublime.ENCODED_POSITION)
			if self.show_traces is False:
				GtagsNavigation().add(path, line, self.symbol)


	def file_preview(self, path, line):
		if path is not None:
			logger.info("preview file: %s:%s", line, path)
			position = '%s:%d:0' % (os.path.normpath(path), int(line))
			sublime.active_window().open_file(position, sublime.ENCODED_POSITION | sublime.TRANSIENT)

	def show(self, panel_list, path_list, event_listener=None):

		if len(path_list) != 0:
			GtagsEventListener().register(event_listener)

			def on_select(index):
				if 'Symbol Traces' in panel_list[0]:
					if index > 0:
						index = index - 1
					GtagsNavigation().set_cur_index(index)

				logger.info("select %d", index)
				if index > 0:
					self.file_jump(path_list[index]["path"], path_list[index]["line"])
				else:
					self.file_jump(path_list[0]["path"], path_list[0]["line"])
				GtagsEventListener().unregister(event_listener)

			def on_highlight(index):
				logger.info("highlight %d", index)
				if index > 0:
					if 'Symbol Traces' in panel_list[0]:
						index = index - 1
					self.file_preview(path_list[index]["path"], path_list[index]["line"])

			#panel_list = [ ["1", "1.1", "1.2"] , ["2", "2.1", "2.2"] ]
			view = sublime.active_window().active_view()
			self.symbol = view.substr(view.word(view.sel()[0].a))

			if 'Symbol Traces' not in panel_list[0]:
				if 'Symbol References' in panel_list[0]:
					logger.info("Symbol Ref")
					self.symbol = "R : " + self.symbol
				else:
					logger.info("Symbol Def")
					self.symbol = "D : " + self.symbol
				GtagsNavigation().add(view.file_name(), view.rowcol(view.sel()[0].a)[0]+1, self.symbol)
			else:
				self.show_traces = True

			sublime.active_window().run_command('hide_overlay')
			logger.info("panel_list len %d", len(panel_list))

			# jump immediately when there is only one item
			if len(panel_list) == 2:
				self.file_jump(path_list[1]["path"], path_list[1]["line"])
			else:
				sublime.active_window().show_quick_panel(panel_list, on_select, 0, -1, on_highlight)




