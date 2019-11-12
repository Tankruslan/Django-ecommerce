from django import forms
from .models import Profile

class ProfileImage(forms.ModelForm):

	image = forms.ImageField(widget=forms.FileInput(attrs={
		'onchange': 'this.form.submit()'
		})
	)

	class Meta:
		model = Profile
		fields = ['image']


class SignupForm(forms.Form):
	first_name = forms.CharField(max_length=50, label=("Имя"),
		widget=forms.TextInput(attrs={'placeholder':('Имя')}))
	last_name = forms.CharField(max_length=50, required=False, label=("Фамилия"),
		widget=forms.TextInput(attrs={'placeholder':('Фамилия')}))

	def signup(self, request, user):
		user.save()