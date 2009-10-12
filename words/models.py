from django.db.models import *

# Everything that goes by the name "code" here is language-
# independant, it is visible only to programmers and is in English
# by convention.

# The following have no significant content, used only for matching
class LanguageKey(Model):
	code = CharField(max_length=6)
	def __unicode__(self):
		return self.code
class CategoryKey(Model):
	code = CharField(max_length=20)
	def __unicode__(self):
		return self.code
class MeaningKey(Model):
	code = CharField(max_length=40)
	def __unicode__(self):
		return self.code
class DictionaryKey(Model): 
	code = CharField(max_length=40)
	def __unicode__(self):
		return self.code

# Names of lexical categories in every language
# Ideally it is the set (LanguageKey x CategoryKey)
class Category(Model):
	# Short form, optional
	short = CharField(max_length=10,null=True)
	# Long form
	long = CharField(max_length=20)
	# Which lexical category? In which language?
	language = ForeignKey(LanguageKey)
	category = ForeignKey(CategoryKey)
	def __unicode__(self):
		return self.language.code + ": " + self.type.code

# hot can be (of temperature) or (of taste)
# Each of these meanings must be in every language
# Ideally this it the set (LanguageKey x MeaningKey)
class Meaning(Model):
	# the text
	text = CharField(max_length=40)
	# Which meaning? In which language?
	language = ForeignKey(LanguageKey)
	meaning = ForeignKey(MeaningKey)
	def __unicode__(self):
		return self.language.code + ": " + self.meaning.code

# Music? Math? Agriculture? Slang?
# Ideally this it the set (LanguageKey x DictionaryKey)
class Dictionary(Model):
	# the text
	text = CharField(max_length=40)
	# Which dictionary? In which language?
	language = ForeignKey(LanguageKey)
	dictionary = ForeignKey(DictionaryKey)
	def __unicode__(self):
		return self.language.code + ": " + self.dictionary.code

class Word(Model):
	# The word itself, in simplest form
	text = CharField(max_length=200,db_index=True)
	# The language of the word
	language = ForeignKey(LanguageKey)
	# Part of speech
	category = ForeignKey(CategoryKey,null=True)
	# Is it a word or a definition
	isword = BooleanField(default=True)
	def __unicode__(self):
		return self.language.code + ": " + self.text

class Concept(Model):
	# The big list of words in each language
	words = ManyToManyField(Word, related_name="concepts")
	# If there are many meanings, which one is used here?
	meaning = ForeignKey(MeaningKey, null=True)
	# Slang? Archaic? Music? Math? Economics?
	dictionary = ForeignKey(DictionaryKey, null=True)

# "Example" merely links the word to the concept, it does not contain
# the actual sentences
class Example(Model):
	# The word
	word = ForeignKey(Word)
	# This example uses the meaning of the word that applies to
	# this concept
	concept = ForeignKey(Concept)

# Every example must have equal sentences in many languages
# each of these sentences deserves a database row
class Sentence(Model):
	# The sentence body
	text = CharField(max_length=100)
	# In which language?
	language = ForeignKey(LanguageKey)
	# For which example?
	example = ForeignKey(Example)
	def __unicode__(self):
		return self.text

