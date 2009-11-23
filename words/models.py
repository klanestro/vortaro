from django.contrib.auth.models import User
from django.db.models import *
from django.db import IntegrityError
# Everything that goes by the name "code" here is language-
# independant, it is visible only to programmers and is in English
# by convention.


class Universal:
	deleted = BooleanField(default=False)

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
class CategoryKey(Model, Universal):
	code = CharField(max_length=20,unique=True)
	def __unicode__(self):
		return self.code
class ConnectionKey(Model, Universal):
	code = CharField(max_length=40,unique=True)
	def __unicode__(self):
		return self.code
class DictionaryKey(Model, Universal): 
	code = CharField(max_length=40,unique=True)
	def __unicode__(self):
		return self.code

class Commit(Model):
	when = DateTimeField(auto_now=True)
	explanation = CharField(max_length=300,null=True)
	language = ForeignKey(LanguageKey,null=True)
	request_approval = BooleanField(default=False)
	# Create, Delete, Modify
	type = CharField(max_length=1)
	# If it was modified, here's the backup id
	backup_id = IntegerField(null=True)
	anonymous = BooleanField(default=False)

# I have to add it now, otherwise the models wouldn't validate
Universal.commits = ManyToManyField(Commit,null=True)

class Editor(User):
	commits = ManyToManyField(Commit,null=True)
	language = ForeignKey(LanguageKey,related_name="editors_prefer",null=True)
	languages = ManyToManyField(LanguageKey,related_name="editors_know",null=True)

## Name of every language in every language
class LanguageName(Model, Universal):
	text = CharField(max_length=30)
	name_of = ForeignKey(LanguageKey,related_name="names")
	name_in = ForeignKey(LanguageKey,related_name="language_names")
	def __unicode__(self):
		return self.name_in.code + "-" + self.name_of.code + ": " + self.text
	
# Names of lexical categories in every language
# Ideally it is the set (LanguageKey x CategoryKey)
class CategoryName(Model, Universal):
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
class ConnectionName(Model, Universal):
	# the text
	text = CharField(max_length=40)
	# Which meaning? In which language?
	language = ForeignKey(LanguageKey)
	meaning = ForeignKey(ConnectionKey)
	def __unicode__(self):
		return self.language.code + ": " + self.meaning.code

# Music? Math? Agriculture? Slang?
# Ideally this it the set (LanguageKey x DictionaryKey)
class DictionaryName(Model, Universal):
	# the text
	text = CharField(max_length=40)
	# Which dictionary? In which language?
	language = ForeignKey(LanguageKey)
	dictionary = ForeignKey(DictionaryKey)
	def __unicode__(self):
		return self.language.code + ": " + self.dictionary.code

class Word(Model, Universal):
	# Usually this is the word itself, however if it is two words,
	# the primary one goes here, and the secondary is omitted
	index = CharField(max_length=70,db_index=True)
	# Full representation
	full = CharField(max_length=70,db_index=True)
	# Broken apart into morphemes (likely to be used only for
	# Esperanto)
	morphemes = CharField(max_length=70)
	# The language of the word
	language = ForeignKey(LanguageKey)
	# Part of speech
	category = ForeignKey(CategoryKey,null=True)
	# Is this an acronym?
	acronym = BooleanField(default=False)
	def __unicode__(self):
		return self.language.code + ": " + self.full
	def concepts(self):
		c = []
		for con in self.concept_connections:
			if not con.concept.deleted:
				c.append(con.concept)
		return c
	def save(self, force_insert=False, force_update=False):
		# Make sure every word is unique
		if Word.objects.filter(full=self.full, language=self.language):
			raise IntegrityError, "This word alreay exists"
		super(Word, self).save(force_insert, force_update)

class Definition(Model, Universal):
	# Full representation
	full = CharField(max_length=70,db_index=True)
	# The language of the definition
	language = ForeignKey(LanguageKey)
	def __unicode__(self):
		return self.language.code + ": " + self.full
	def save(self, force_insert=False, force_update=False):
		# Make sure every Definition is unique
		if Definition.objects.filter(full=self.full,
				language=self.language):
			raise IntegrityError, "This definition alreay exists"
		super(Definition, self).save(force_insert, force_update)

class Concept(Model, Universal):
	# The big list of words in each language
	words = ManyToManyField(Word, related_name="concepts")
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
class ConceptConnection(Model, Universal):
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
class WordConnection(Model, Universal):
	word = ForeignKey(Word, related_name="derivatives")
	derivative = ForeignKey(Word, related_name="derived_from")

class Example(Model, Universal):
	# Example for this concept 
	concept = ForeignKey(Concept,related_name="examples")

# Every example must have equal sentences in many languages
# each of these sentences deserves a database row
class Sentence(Model, Universal):
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


