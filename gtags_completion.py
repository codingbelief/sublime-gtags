import sublime
import sublime_plugin
import logging
import SublimeGtags.gtags_project
import SublimeGtags.gtags_symbol
import SublimeGtags.gtags_event


from SublimeGtags.gtags_symbol import *
from SublimeGtags.gtags_event import *

from SublimeGtags.gtags_project import *
from sublime_plugin import all_callbacks

logging.basicConfig(format="[%(asctime)s] - [%(name)s] - [%(levelname)s] - \n%(message)s\n")
logger = logging.getLogger('Completion')
logger.setLevel(logging.DEBUG)

class GtagsCompletion(object):

	is_started  = False
	start_point = {'view':0, "prefix":0, "locations":0}
	last_prefix = "!"
	completions = []

	def get_completions(self):
		return self.completions

	def cleanup(self):
		self.completions = []
		self.is_started  = False
		self.last_prefix = "!"
		self.start_point = {'view':0, "prefix":0, "locations":0}
		GtagsEventListener().unregister(self)

	def on_selection_modified_async(self,view):
		#print("on_selection_modified_async", view.sel()[0])
		#print(view.substr(view.word(view.sel()[0])))
		#print(view.word(view.sel()[0]).a)

		# do nothing if the auto_completion popup is not showed
		if self.is_started == False:
			logger.info("not started")
			return

		# cleanup when switchs to another view
		if self.start_point["view"] != view:
			self.cleanup()
			logger.info("not the same view")
			return

		# cleanup when focus on another word
		prefix_start = self.start_point["locations"][0] - len(self.start_point["prefix"])
		try:
			if prefix_start != view.word(view.sel()[0]).a:
				self.cleanup()
				logger.info("not the same word")
				return
		except IndexError:
				self.cleanup()
				logger.info("IndexError when check if the same word")
				return

		# cleanup when there is no prefix
		try:
			if prefix_start == view.sel()[0].a:
				self.cleanup()
				logger.info("no prefix")
				return
		except IndexError:
				self.cleanup()
				logger.info("IndexError when check if no prefix")
				return


		# search the completions only when the len of prefix >= 3
		if view.sel()[0].a - prefix_start >= 3:

			cur_prefix = view.substr(sublime.Region(prefix_start, view.sel()[0].a))
			logger.info("last prefix: %s, cur prefix: %s",self.last_prefix, cur_prefix)

			# if the completion has got before, do not search again
			if cur_prefix.find(self.last_prefix) != 0:
				logger.info("get the completions prefix: %s", cur_prefix)

				self.last_prefix  = cur_prefix
				self.completions = GtagsSymbol().get_completions(cur_prefix)
				#print(self.completions, len(self.completions))
				if len(self.completions) > 0:
					sublime.set_timeout_async(self.show_completions, 0)
			return
		logger.info("nothing to do view.sel: %s, prefix_start: %s", view.sel()[0].a, prefix_start)

	def is_need_to_show(self, view, prefix, locations):
		if (self.is_started == False) and (len(prefix) != 0):
			logger.info("completions start: [prefix]:%s, [locations]:%s",prefix, locations)
			self.start_point["view"]      = view
			self.start_point["prefix"]    = prefix
			self.start_point["locations"] = locations
			self.is_started = True
			self.on_selection_modified_async(view)
			GtagsEventListener().register(self)
		return len(self.completions) > 0

	def show_completions(self):
		logger.info("show_completions")
		#sublime.active_window().run_command("hide_auto_complete")
		#sublime.active_window().run_command('auto_complete')
