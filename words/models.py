from django.contrib.auth.models import User
from django.db.models import *
from django.db import IntegrityError
from django.forms.models import model_to_dict

# Everything that goes by the name "code" here is language-
# independant, it is visible only to programmers and is in English
# by convention.


class Universal(Model):
	deleted = BooleanField(default=False)
	hidden = BooleanField(default=False)
	def button(self):
		"""
		Returns an HTML representation of the object
		"""
		return button(self)
	def values(self):
		"""
		obj.values() is equivalent to model_to_dict(obj). I think that this
		definitely belongs in the list of standard methods of a Model
		"""
		return model_to_dict(self)
		
	def backup(self):
		"""
		This function is used to create backups. It returns the id of the clone.
		"""
		# Get all fields
		fields = self.__dict__.copy()
		# Set backup to be hidden
		fields["hidden"] = True
		# Get rid of the id and any underscored garbage
		for key in fields.keys():
			if key.startswith("_") or key == "id":
				del fields[key]
		# Commence cloning...
		backup = self.__class__(**fields)
		backup.save()
		return backup.id
	class Meta:
		abstract = True

# The following have no significant content, used only for matching
class LanguageKey(Model):
	code = CharField(max_length=6,unique=True)
	def __unicode__(self):
		return self.code
	def getname(self,key):
		if not isinstance(key, LanguageKey):
			key = LanguageKey.objects.get(code=key)
		name = self.names.filter(name_in=key)
		if not name:
			return self.code
		return name[0].text
class CategoryKey(Universal):
	code = CharField(max_length=20,unique=True)
	def __unicode__(self):
		return self.code
class ConnectionKey(Universal):
	code = CharField(max_length=40,unique=True)
	def __unicode__(self):
		return self.code
class DictionaryKey(Universal): 
	code = CharField(max_length=40,unique=True)
	def __unicode__(self):
		return self.code

## Name of every language in every language
class LanguageName(Universal):
	text = CharField(max_length=30)
	name_of = ForeignKey(LanguageKey,related_name="names")
	name_in = ForeignKey(LanguageKey,related_name="language_names")
	def __unicode__(self):
		return self.name_in.code + "-" + self.name_of.code + ": " + self.text
	
# Names of lexical categories in every language
# Ideally it is the set (LanguageKey x CategoryKey)
class CategoryName(Universal):
	# Short form, optional
	short = CharField(max_length=10,null=True)
	# Long form
	long = CharField(max_length=20)
	# Which lexical category? In which language?
	language = ForeignKey(LanguageKey)
	category = ForeignKey(CategoryKey)
	def __unicode__(self):
		return self.language.code + ": " + self.type.code

# hot can be (of temperature), (of taste) or (slang)
# Each of these meanings must be in every language
# Ideally this it the set (LanguageKey x ConnectionKey)
class ConnectionName(Universal):
	# the text
	text = CharField(max_length=40)
	# Which meaning? In which language?
	language = ForeignKey(LanguageKey)
	meaning = ForeignKey(ConnectionKey)
	def __unicode__(self):
		return self.language.code + ": " + self.meaning.code

# Music? Math? Agriculture? Slang?
# Ideally this it the set (LanguageKey x DictionaryKey)
class DictionaryName(Universal):
	# the text
	text = CharField(max_length=40)
	# Which dictionary? In which language?
	language = ForeignKey(LanguageKey)
	dictionary = ForeignKey(DictionaryKey)
	def __unicode__(self):
		return self.language.code + ": " + self.dictionary.code

class Word(Universal):
	def __unicode__(self):
		return self.full
	# Full representation
	full = CharField(max_length=70,db_index=True)
	# Broken apart into morphemes (likely to be used only for
	# Esperanto)
	morphemes = CharField(max_length=70,null=True)
	# The language of the word
	language = ForeignKey(LanguageKey)
	# Part of speech
	category = ForeignKey(CategoryKey,null=True)
	# Is this an acronym?
	acronym = BooleanField(default=False)
	def concepts(self):
		c = []
		for con in self.concept_connections:
			if not con.concept.deleted:
				c.append(con.concept)
		return c

class Definition(Universal):
	# Full representation
	full = CharField(max_length=70,db_index=True,null=True)
	# The language of the definition
	language = ForeignKey(LanguageKey,null=True)
	def __unicode__(self):
		return self.language.code + ": " + self.full
	def save(self, force_insert=False, force_update=False):
		# Make sure every Definition is unique
		if Definition.objects.filter(full=self.full,
				language=self.language):
			raise IntegrityError, "This definition alreay exists"
		super(Definition, self).save(force_insert, force_update)

class Concept(Universal):
	# Music? Math? Economics?
	dictionary = ManyToManyField(DictionaryKey, null=True)
	# Antonym links to another concept
	antonym = OneToOneField('self',null=True)
	def words(self):
		c = []
		for con in self.word_connections:
			if not con.word.deleted:
				c.append(con.word)
		return c

# A connection between a concept and a word
class ConceptConnection(Universal):
	word = ForeignKey(Word,related_name="concept_connections")
	concept = ForeignKey(Word,related_name="word_connections")
	# slang? archaic?
	key = ForeignKey(ConnectionKey,null=True)
	# Clarification in brackers. Eg. hot (of flavour)
	# Must be in same language as word
	clarification = CharField(max_length=70,null=True)
	# Before of after the word
	clarification_before = BooleanField(default=False)

# A connection between a word and its derivative
class WordConnection(Universal):
	word = ForeignKey(Word, related_name="derivatives")
	derivative = ForeignKey(Word, related_name="derived_from")

class Example(Universal):
	# Example for this concept 
	concept = ForeignKey(Concept,related_name="examples")

# Every example must have equal sentences in many languages
# each of these sentences deserves a database row
class Sentence(Universal):
	# The sentence body
	text = CharField(max_length=100)
	# In which language?
	language = ForeignKey(LanguageKey)
	# For which example?
	connection = ForeignKey(Example,related_name="sentences")
	def __unicode__(self):
		return self.text
	def save(self, force_insert=False, force_update=False):
		# Make sure every sentence is unique
		if Sentence.objects.filter(full=self.full,
				language=self.language):
			raise IntegrityError, "This sentence alreay exists"
		super(Person, self).save(force_insert, force_update)

#from vortaro.words.actions import EditorActions
class Editor(User):
	language = ForeignKey(LanguageKey,related_name="editors_prefer",null=True)
	languages = ManyToManyField(LanguageKey,related_name="editors_know",null=True)
	def __unicode__(self):
		text = self.first_name + " " + self.last_name
		text = text.strip()
		if not text:
			text = u"Anonymous"
		return text
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
		w = Word()
		self._modify(w, values)
		w.save()
		commit = Commit(
			editor = self,
			commit_type = "cw",
			object_id = w.id)
		commit.save()
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

class Commit(Model):
	when = DateTimeField(auto_now=True)
	explanation = CharField(max_length=300,null=True)
	wait_approval = BooleanField(default=False)
	# Create, Delete, Modify
	commit_type = CharField(max_length=2)
	# If it was created or deleted, here's the object id
	object_id = IntegerField(null=True)
	# If it was modified, here's the backup id	
	backup_id = IntegerField(null=True)
	# Who did it
	editor = ForeignKey(Editor,related_name="commits")
	
# I have to add it now, otherwise the models wouldn't validate
Universal.commits = ManyToManyField(Commit,null=True)

def button(obj):
	"""
	Creates an embeddable link button for an object such as Word or Sentence.
	Takes the object as an argument.
	"""
	c = "button"
	if obj.deleted:
		c = "button deleted"
	if isinstance(obj, Word):
		name = ("word","W")
		return """
		<span class="%s">
		<span class="button_id" title="#%d">#</span>
		<a href="/data/word/%d">%s</a></span>
		""" % (c, obj.id, obj.id, unicode(obj))
	else: return ""
	return """
	<span class="%s"><a href="/data/%s/%d">%s%d</a></span>
	""" % (c, name[0], obj.id, name[1], obj.id)
