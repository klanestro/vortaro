from django import forms
from vortaro.words.models import *
	
class ManyLanguagesField(forms.ModelMultipleChoiceField):
	def label_from_instance(self, obj):
		return obj.getname("eng")
	
class LanguageField(forms.ModelChoiceField):
	def label_from_instance(self, obj):
		return obj.getname("eng")

class RegisterForm(forms.Form):
	email = forms.EmailField(max_length=100)
	def clean(self):
		if "email" not in self.cleaned_data:
			return self.cleaned_data
		try:
			old_user = Editor.objects.get(email=self.cleaned_data["email"])
			raise forms.ValidationError("A user with this email already exists")
		except Editor.DoesNotExist:
			return self.cleaned_data

class SettingsForm(forms.Form):
	first_name = forms.CharField(
		max_length = 30,
		required = False,
		widget = forms.TextInput(attrs={"autocomplete":"off"}))
	last_name = forms.CharField(
		max_length = 30,
		required = False,
		widget = forms.TextInput(attrs={"autocomplete":"off"}))
	#language = LanguageField(
	#	queryset=LanguageKey.objects.all(),
	#	label="Preferred language",
	#	required=False
	#)
	languages = ManyLanguagesField(
		queryset = LanguageKey.objects.all(),
		label = "Working languages",
		required = False,
		help_text = "You can choose multiple languages by holding down the shift key")
	p1 = forms.CharField(
		max_length = 30,
		required = False,
		widget = forms.PasswordInput(attrs={"autocomplete":"off"}),
		label = "New password")
	p2 = forms.CharField(
		max_length = 30,
		required = False,
		widget = forms.PasswordInput(attrs={"autocomplete":"off"}),
		label = "Retype")
	def clean(self):
		cleaned_data = self.cleaned_data
		p1 = cleaned_data['p1']
		p2 = cleaned_data['p2']
		if p2 and p1 != p2:
			raise forms.ValidationError("Entered passwords do not match")
		else:
			cleaned_data["password"] = p2
		return cleaned_data

class LoginForm(forms.Form):
	email = forms.EmailField(max_length=100)
	password = forms.CharField(max_length=30,widget=forms.PasswordInput)
	
class WordForm(forms.Form):
	language = LanguageField(queryset=LanguageKey.objects.all())
	full = forms.CharField(max_length=70,required=False)
	id = forms.IntegerField(widget=forms.HiddenInput,required=False)
