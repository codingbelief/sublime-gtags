

import sublime
import sublime_plugin
import logging
import os

logging.basicConfig(format="[%(asctime)s] - [%(name)s] - [%(levelname)s] - \n%(message)s\n")
logger = logging.getLogger('Project')
logger.setLevel(logging.DEBUG)

class GtagsProject(object):

	name=None

	def get_pwd(self, file_path):
		project = sublime.active_window().project_data()
		if project is None:
			logger.info("No active project!")
			if file_path is None:
				logger.info("No active file!")
				return "./"
			return os.path.realpath(os.path.dirname(file_path))

		folders = project.get('folders')
		if folders is None:
			logger.info("No active folders!")
			if file_path is None:
				logger.info("No active file!")
				return "./"
			return os.path.realpath(os.path.dirname(file_path))

		if file_path is None:
			return os.path.realpath(folders[0].get('path'))

		file_path = os.path.realpath(file_path)
		for folder in folders:
			folder_path = os.path.realpath(folder.get('path'))
			if folder_path in file_path:
				logger.info("PWD is %s", folder_path)
				return folder_path

		return os.path.realpath(folders[0].get('path'))


	def get_config(self):

		project = sublime.active_window().project_data()
		if project is None:
			logger.warning("no active project!")
			return {}

		config = project.get('gtags_config')

		if config is None:
			gtagsroot = ""
			gtagslibs = []

			logger.warning("can not find gtags_config in the project setting, \
				            using the project folders path")

			folders   = project.get('folders')

			gtagsroot = folders[0].get('path')
			for folder in folders:
				gtagslibs.append(os.path.normpath(folder.get('path')))
			return {'GTAGSROOT': gtagsroot, 'GTAGSLIBPATH': gtagslibs}
			#return {'GTAGSLIBPATH': gtagslibs}
		else:
			logger.info("get the config %s", config)
			return config

	def is_changed(self):

		name = sublime.active_window().project_file_name()

		ret = False
		if GtagsProject.name is not None:
			if name is None or GtagsProject.name != name:
				GtagsProject.name = name
				logger.info("project switch from %s to %s", GtagsProject.name, name)
				ret = True
		else:
			if name is not None:
				GtagsProject.name = name
				logger.info("project switch from %s to %s", GtagsProject.name, name)
				ret = True
		return ret

	def is_file_in_project(self, file_path):

		project = sublime.active_window().project_data()
		folders = project.get('folders')

		if file_path is None:
			return False
		file_path = os.path.realpath(file_path)
		for folder in folders:
			folder_path = os.path.realpath(folder.get('path'))
			if folder_path in file_path:
				logger.info("parent project is %s", folder_path)
				return True

		return False

	def get_gtags_paths(self):
		paths = []
		project = sublime.active_window().project_data()
		folders = project.get('folders')
		logger.debug("project folders: %s", folders)
		for folder in folders:
			folder_path = os.path.realpath(folder.get('path'))
			gtags_path  = os.path.join(folder_path, "GTAGS")
			logger.debug("test gtags path: %s !", gtags_path)
			if os.path.isfile(gtags_path):
				logger.debug("get gtags path: %s", gtags_path)
				paths.append(folder_path)
		return paths


