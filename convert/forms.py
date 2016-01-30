from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserForms(forms.Form):
    username = forms.CharField(label='Username', max_length=10)
    password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super(UserForms, self).clean()
        passw = cleaned_data.get('password')
        try:
            u = User.objects.get(username=cleaned_data.get('username'))
        except User.DoesNotExist:
            self.add_error('username', "Sorry, wrong username or password!")
            return
        if any(self.errors):
            self.add_error('password', "Sorry, wrong username or password!")
            return


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=30)

    class Meta:
        model = User
        fields = ("username", "email",)

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user