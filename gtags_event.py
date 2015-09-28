
import sublime
import sublime_plugin
import logging
from sublime_plugin import all_callbacks

logging.basicConfig(format="[%(asctime)s] - [%(name)s] - [%(levelname)s] - \n%(message)s\n")
logger = logging.getLogger('Event')
logger.setLevel(logging.DEBUG)


class GtagsEventListener(object):

	def register(self, obj):
		event_cnt = 0
		for event in all_callbacks.items():
			if event[0] in dir(obj):
				event[1].append(obj)
				event_cnt = event_cnt + 1
				logger.info("listens on %s event, callback: %s", event[0], obj)
		return event_cnt

	def unregister(self, obj):
		event_cnt = 0
		for event in all_callbacks.items():
			if event[0] in dir(obj):
				try:
					event[1].remove(obj)
					event_cnt = event_cnt + 1
				except :
					sublime.error_message("fail when remove %s event, callback: %s" % (event[0], obj))
				logger.info("remove %s event, callback: %s", event[0], obj)
		return event_cnt


