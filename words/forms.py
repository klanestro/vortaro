from django import forms
from vortaro.words.models import *

class RegisterForm(forms.Form):
	email = forms.EmailField(max_length=100)
	
class ManyLanguagesField(forms.ModelMultipleChoiceField):
	def label_from_instance(self, obj):
		return obj.getname("eng")
	
class LanguageField(forms.ModelChoiceField):
	def label_from_instance(self, obj):
		return obj.getname("eng")

class SettingsForm(forms.Form):
	first_name = forms.CharField(max_length=30,required=False)
	last_name = forms.CharField(max_length=30,required=False)
	#language = LanguageField(
	#	queryset=LanguageKey.objects.all(),
	#	label="Preferred language",
	#	required=False
	#)
	languages = ManyLanguagesField(
		queryset=LanguageKey.objects.all(),
		label="Working languages",
		required=False,
		#widget=forms.CheckboxSelectMultiple,
		help_text="You can choose multiple languages by holding down the shift key"
	)
	p1 = forms.CharField(
		max_length=30,
		required=False,
		widget=forms.PasswordInput,
		label="New password",
	)
	p2 = forms.CharField(
		max_length=30,
		required=False,
		widget=forms.PasswordInput,
		label="Retype",
	)
	def clean(self):
		cleaned_data = self.cleaned_data
		p1 = cleaned_data['p1']
		p2 = cleaned_data['p2']
		if p2 and p1 != p2:
			raise forms.ValidationError("Entered passwords do not match")
		else:
			cleaned_data["password"] = p2
		return cleaned_data
			
