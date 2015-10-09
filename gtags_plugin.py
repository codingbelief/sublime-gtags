import sublime
import sublime_plugin
import SublimeGtags.gtags_project
import SublimeGtags.gtags_symbol
import SublimeGtags.gtags_ui
import SublimeGtags.gtags_completion
import SublimeGtags.gtags_navigation
import logging
from SublimeGtags.gtags_navigation import GtagsNavigation
from SublimeGtags.gtags_symbol import GtagsSymbol
from SublimeGtags.gtags_ui import GtagsUIQuickPanel
from SublimeGtags.gtags_completion import *
from SublimeGtags.gtags_project import GtagsProject

from sublime_plugin import all_callbacks


logging.basicConfig(format="[%(asctime)s] - [%(name)s] - [%(levelname)s] - \n%(message)s\n")
logger = logging.getLogger('Plugin')
logger.setLevel(logging.DEBUG)


class GtagsBuildTagsCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], newLeaf = False):
		logger.info("run GtagsBuildTags!")
		logger.info("%s", paths)
		GtagsSymbol().build_tags(paths[0])

class GtagsForward(sublime_plugin.TextCommand):

	def run(self, edit):
		GtagsNavigation().forward()

class GtagsBackward(sublime_plugin.TextCommand):

	def run(self, edit):
		GtagsNavigation().backward()

class GtagsShowTrace(sublime_plugin.TextCommand):

	def run(self, edit):

		logger.info("run GtagsShowTrace!")
		sublime.set_timeout_async(self.show_trace, 1)

	def show_trace(self, name=None):

		sublime.status_message('Getting trace ...............................')
		traces = GtagsNavigation().show_trace()
		logger.info("trace: %s!", traces)

		if len(traces) == 0:
			sublime.status_message('No trace')
		else:

			panel_list = [
			        	    [
			                	"  " + trace["symbol"],
			                	"  " + trace["path"],
			                ]
			                for trace in traces
			             ]
			# the first item is used as a title
			panel_list[0:0] = [["Symbol Traces","%d" % len(traces)]]
			#traces[0:0] = [{"path":self.view.file_name(), "line":self.view.rowcol(self.view.sel()[0].a)[0]+1}]
			sublime.status_message('Gtags Show Traces')
			GtagsUIQuickPanel().show(panel_list, traces)

class GtagsTrace(sublime_plugin.TextCommand):

	def run(self, edit):
		GtagsNavigation().add(self.view.file_name(), self.view.rowcol(self.view.sel()[0].a)[0]+1)

class GtagsJumpToDefinitionCommand(sublime_plugin.TextCommand):
	symbol_name = None

	def run(self, edit):

		logger.info("run GtagsJumpToDefinitionCommand!")
		# get current word
		self.symbol_name = self.view.substr(self.view.word(self.view.sel()[0].a))
		if len(self.symbol_name) != 0:
			sublime.set_timeout_async(self.jump_to_definition, 1)

	def jump_to_definition(self, name=None):

		if name is not None:
			self.symbol_name = name

		sublime.status_message('Definitions searching ...............................')
		definitions = GtagsSymbol().get_definitions(self.symbol_name, self.view.file_name())
		logger.info("get definitions of symbol: %s, %s!", self.symbol_name, definitions)

		if len(definitions) == 0:
			sublime.status_message('Sublime Definitions')
			sublime.active_window().run_command("goto_definition")
		else:
			'''
			panel_list = [
			        	    [
			                	"  "+os.path.basename(definition["path"]),
			                	"         " + definition["signature"],
			                	"         " + definition["path"]
			                ]
			                for definition in definitions
			             ]
			# the first item is used as a title
			panel_list[0:0] = [["Symbol Definitions","%d" % len(definitions), self.view.file_name()]]
			definitions[0:0] = [{"path":self.view.file_name(), "line":self.view.rowcol(self.view.sel()[0].a)[0]+1}]
			'''
			panel_list = [
			        	    [
			                	"  "+os.path.basename(definition["path"]) + "    : " + definition["path"],
			                	"                           " + definition["signature"],
			                ]
			                for definition in definitions
			             ]
			# the first item is used as a title
			panel_list[0:0] = [["Symbol Definitions","%d" % len(definitions)]]
			definitions[0:0] = [{"path":self.view.file_name(), "line":self.view.rowcol(self.view.sel()[0].a)[0]+1}]
			sublime.status_message('Gtags Definitions')
			GtagsUIQuickPanel().show(panel_list, definitions)


class GtagsJumpToReferenceCommand(sublime_plugin.TextCommand):
	symbol_name = None

	def run(self, edit):
		logger.info("run GtagsJumpToDefinitionCommand!")
		# get current word
		self.symbol_name = self.view.substr(self.view.word(self.view.sel()[0].a))
		if len(self.symbol_name) != 0:
			sublime.set_timeout_async(self.jump_to_reference, 1)

	def jump_to_reference(self, name=None):

		if name is not None:
			self.name = name

		sublime.status_message('References searching ...............................')
		references = GtagsSymbol(self.view.file_name()).get_references(self.symbol_name)
		logger.info("get references of symbol: %s, %s!", self.symbol_name, references)

		if len(references) == 0:
			sublime.status_message('Sublime References')
			self.view.window().run_command("goto_definition")
		else:
			'''
			panel_list = [
			        	    [
			                	"  "+os.path.basename(reference["path"]),
			                	"         " + reference["signature"],
			                	"         " + reference["path"]
			                ]
			                for reference in references
			             ]
			# the first item is used as a title
			panel_list[0:0] = [["Symbol References","%d" % len(references), self.view.file_name()]]
			references[0:0] = [{"path":self.view.file_name(), "line":self.view.rowcol(self.view.sel()[0].a)[0]+1}]
			'''
			panel_list = [
			        	    [
			                	"  "+os.path.basename(reference["path"]) + "    : " + reference["path"] + "    : " + reference["signature"],
			                	"                           " + reference["signature"],
			                ]
			                for reference in references
			             ]
			# the first item is used as a title
			panel_list[0:0] = [["Symbol References","%d" % len(references)]]
			references[0:0] = [{"path":self.view.file_name(), "line":self.view.rowcol(self.view.sel()[0].a)[0]+1}]
			sublime.status_message('Gtags References')
			GtagsUIQuickPanel().show(panel_list, references)



class GtagsListDefinitionsOfFileCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		logger.info("run GtagsJumpToDefinitionCommand!")
		sublime.set_timeout_async(self.list_definitions, 1)

	def list_definitions(self):
		sublime.status_message('Definitions searching ...............................')
		definitions = GtagsSymbol(self.view.file_name()).get_all_symbol_definitions_of_file(self.view.file_name())
		if len(definitions) == 0:
			sublime.status_message('Sublime Definitions')
			self.view.window().run_command("show_overlay", {"overlay": "goto", "text": "@"})
		else:
			panel_list = [
			                [
			                	"  "+os.path.basename(definition["symbol"]),
			                	"         " + definition["signature"]
			                ]
			                for definition in definitions
			             ]
			# the first item is used as a title
			panel_list[0:0]  = [["Definitions", "%d" % len(definitions)]]
			definitions[0:0] = [{"path":self.view.file_name(), "line":self.view.rowcol(self.view.sel()[0].a)[0]+1}]
			sublime.status_message('Gtags Definitions')
			GtagsUIQuickPanel().show(panel_list, definitions)


class GtagsLookupDefinitionCommand(sublime_plugin.TextCommand):
	symbol_name = None
	index       = None
	basic_view   = None
	completions_panel_list  = None
	cur_file = None
	def run(self, edit):
		self.cur_file = self.view.file_name()
		logger.info("run GtagsLookupDefinitionCommand!")
		GtagsLookupDefinitionCommand.basic_view = self.view
		sublime.set_timeout_async(self.lookup_definition, 1)

	def show_definition_panel(self):
		view = GtagsLookupDefinitionCommand.basic_view
		logger.info("basic view: %s, file_name: %s", view, view.file_name())
		GtagsJumpToDefinitionCommand(view).jump_to_definition(self.completions_panel_list[self.index])

	def on_modified(self, view):

		prefix = view.substr(view.word(view.sel()[0]))
		logger.info("current prefix: %s", prefix)

		locations = [0]
		locations[0] = view.sel()[0].a

		if len(prefix) >= 3:
			if GCompletion.is_need_to_show(view, prefix, locations) == False:
				logger.info("not enough prefix")
			else:
				logger.info("lookup_definition definitions prefix: %s", prefix)
				sublime.status_message('Definitions searching ...............................')
				completions = GCompletion.get_completions()
				#view.show(locations[0])
				logger.info("completions: %s", completions)
				sublime.status_message('Gtags Definitions')

				def on_select(index):
					logger.info("select %d", index)
					if index != -1:
						self.index = index
						sublime.set_timeout_async(self.show_definition_panel, 100)

				def on_highlight(index):
					logger.info("highlight %d", index)

				self.completions_panel_list = [ m[1] for m in completions ]
				logger.info("self.completions_panel_list %s", self.completions_panel_list)
				view.window().run_command('hide_overlay')
				sublime.active_window().show_quick_panel(self.completions_panel_list, on_select, 0, -1, on_highlight)

	def lookup_definition(self):
		definitions = []
		panel_list  = []
		panel_list[0:0] = [["Definitions", "%d" % len(definitions)]]
		definitions[0:0] = [{"path":self.view.file_name(), "line":self.view.rowcol(self.view.sel()[0].a)[0]+1}]
		GtagsUIQuickPanel().show(panel_list, definitions, self)


GCompletion = GtagsCompletion()
class GtagsCompletionListenerCommand(sublime_plugin.EventListener):

	def on_query_completions(self, view, prefix, locations):
		logger.info("on_query_completions prefix: %s", prefix)

		if not view.match_selector(locations[0],
			"source.c, source.c++, source.objc, source.objc++"):
			return []

		if GCompletion.is_need_to_show(view, prefix, locations) == False:
			#logger.info("return completions: %s", [("uuuuu", "uuuuu")])
			#return ([("uuuuu", "uuuuu")])
			return []

		sublime.status_message('Completions searching ...............................')
		completions = GCompletion.get_completions()
		sublime.status_message('Gtags Completions')

		#return (completions, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)
		return (completions)


'''
class GtagsCompletionTEST(sublime_plugin.EventListener):

	def on_selection_modified_async(self,view):
		print(view.id())
'''
class GtagsUpdateTags(sublime_plugin.TextCommand):

	def run(self, edit):
		ret = 0;
		ret = GtagsSymbol(self.view.file_name()).update(self.view.file_name())
		if ret == 0:
			logger.info("UpdateTags successfully")
			sublime.status_message('Gtags UpdateTags Successfully')
		else:
			logger.info("UpdateTags failed")
			sublime.status_message('Gtags UpdateTags Failed')

class GtagsVersion(sublime_plugin.TextCommand):
	def run(self, edit):
		GtagsSymbol(self.view.file_name()).version(self.view.file_name())

class GtagsSingleFileUpdateTags(sublime_plugin.TextCommand):

	def run(self, edit):
		ret = 0;
		ret = GtagsSymbol(self.view.file_name()).sfupdate(self.view.file_name())
		if ret == 0:
			logger.info("Single File UpdateTags successfully")
			sublime.status_message('Gtags Single File UpdateTags Successfully')
		else:
			logger.info("Single File UpdateTags failed")
			sublime.status_message('Gtags  Single File UpdateTags Failed')

class GtagsAutoUpdateTags(sublime_plugin.EventListener):

	def on_post_save(self, view):
		ret = 0;
		ret = GtagsSymbol(view.file_name()).file_changed(view.file_name())
		if ret == 0:
			logger.info("Auto Single File UpdateTags successfully")
			sublime.status_message('Gtags Auto Single File UpdateTags Successfully')
		elif ret == -2:
			logger.info("Auto Single File UpdateTags failed: file not in project")
			sublime.status_message('Gtags file not in project')
		else:
			logger.info("Auto Single File UpdateTags failed")
			sublime.status_message('Gtags Auto Single File UpdateTags Failed')


