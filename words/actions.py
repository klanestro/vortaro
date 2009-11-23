from vortaro.words.models import *

class EditorActions:
	def _modify(self, obj, newvals):
		"""
		Takes any object and a dict of new values and overwrites each. It 
		ignores values that the object can't take. Returns True if at least
		one new value was given, otherwise False.
		"""
		changed = False
		for key, val in newvals.items():
			if key == "id": continue
			try:
				if not changed and obj.__getattribute__(key) != val:
					changed = True
				obj.__setattr__(key, val)
			except: pass
		return changed

	def create_word(self, values):
		"""
		Creates a word with given values and returns its instance.
		"""
		w = Word(**values)
		#self._modify(w, values)
		w.save()
		commit = Commit(
			commit_type = "cw",
			object_id = w.id)
		return w

	def modify_word(self, word, values, explanation=None, 
			wait_approval=False):
		"""
		Takes an Editor, Word and a dict of values as parameters. Modifies the
		word, creating a Commit
		"""
		# Modify and return False if nothing new was done.
		if not self._modify(word, values):
			return False
		
		#commit = Commit(
		#	commit_type = "mw",
		#	object_id = word.id,
		#	backup_id = word.backup())
		
		word.save()
		return True
		
		
