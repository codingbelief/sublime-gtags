import sublime, sublime_plugin
import shlex, subprocess, os


class GtagsTestPopupMenuCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		window = sublime.active_window()
		view = window.active_view()
		#if not self.output_view:
		data = ["1", "2", "3"]
		def on_done(index):
			print(index)
		view.show_popup_menu(data, on_done)

class GtagsTestOutputPanelCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		window = sublime.active_window()
		view = window.active_view()
		#if not self.output_view:
		self.output_view = window.create_output_panel("test")
		window.run_command('show_panel', {'panel': 'output.test'})

class GtagsTestInputPanelCommand(sublime_plugin.TextCommand):
	def run(self, param=None):
		window = sublime.active_window()
		view = window.active_view()
		print(window)
		window.show_input_panel("Enter something", "test", self.on_done, self.on_change, None)

	def on_done(self, result):
		print("result", result)

	def on_change(self, text):
		print("current text", text)


class GtagsTestQuickPanelCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		window = sublime.active_window()
		view = window.active_view()
		data = [["1","1.1",], "2", "3"]
		def on_select(index):
			print(index)
		def on_highlight(index):
			print("on_highlight %d" % index)
		view.window().show_quick_panel(data, on_select, 0, -1, on_highlight)

class GtagsTestDefCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		print("test match main")
		f = Global.gtags.TagFile("D:\SourceCode\globa")
		matches = f.match("main")
		print(len(matches))
		for match in matches :
			print(match)

class GtagsTestStartWithCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		print("test start_with ma")
		f = Global.gtags.TagFile("D:\SourceCode\globa")
		matches = f.start_with("ma")
		print(len(matches))
		for match in matches :
			print(match)

class GtagsTestRefCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		print("test reference")
		f = Global.gtags.TagFile("D:\SourceCode\globa")
		matches = f.match("main", reference=True)
		print(len(matches))
		for match in matches :
			print(match)

class GtagsTestCommand(sublime_plugin.TextCommand, sublime_plugin.WindowCommand):
	def run(self, edit):

		#BIN_PATH     = "/opt/local/bin/"
		BIN_PATH = "/Users/RockZhang/Library/Application Support/Sublime Text 3/Packages/SublimeGtags/bin/Darwin"
		command_line = "global -ax main"
		args = shlex.split(command_line)
		print(args)

		exec_env = {}
		#exec_env['PATH'] = os.environ['PATH']
		exec_env['PATH'] = os.path.normpath(BIN_PATH)

		#subprocess.call('ping 127.0.0.1')
		PROJECT_PATH = "/Users/RockZhang/Documents/SourceCode/barebox-2013.06.0"
		h = subprocess.Popen(args, \
			                #shell=True,       \
			                env=exec_env,            \
							stdin=subprocess.PIPE,   \
							stdout=subprocess.PIPE,  \
							stderr=subprocess.PIPE,  \
							cwd=PROJECT_PATH,        \
							universal_newlines=True) \
		#h = subprocess.Popen(args)

		for i in range(5):
			line = h.stdout.readline()
			print(line)
			resultlist = line.split(' ')
			while '' in resultlist:
				resultlist.remove('')
			print(resultlist)
		h.kill()


