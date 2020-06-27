"""
Definition of forms.
"""

from django import forms
from django.forms import ModelForm, modelformset_factory
from django.contrib.auth.forms import AuthenticationForm, AdminPasswordChangeForm
from django.contrib.auth.forms import (
    UserCreationForm as DjangoUserCreationForm)
from django.utils.translation import ugettext_lazy as _
from . import models
from django.contrib.auth.forms import UsernameField
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from bootstrap_modal_forms.forms import BSModalForm



class AuthenticationForm(forms.Form):
    """Authentication form which uses boostrap CSS."""
    email = forms.EmailField(widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Email'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

    def __init__(self,request=None,*args,**kwargs):
        self.request=request
        self.User=None
        super().__init__(*args,**kwargs)

    def clean(self):
        email=self.cleaned_data.get("email")
        password=self.cleaned_data.get("password")

        if email is not None and password:
            self.user = authenticate(self.request,email=email,password=password)
            if self.user is None:
                raise forms.ValidationError("Invalid email/password combination.")

        return self.cleaned_data

    def get_user(self):
        return self.user

class UserCreationForm(DjangoUserCreationForm):

    model=models.User

    first_name=forms.CharField(widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'First Name'}))

    last_name=forms.CharField(widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Last Name'}))

    email = forms.EmailField(widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Email'}))

    password1 = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

    password2 = forms.CharField(label=_("Re-Type Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Re-Type Password'}))


    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Re-Type Password'})

    def send_mail(self):
        admin=models.User.objects.get(is_superuser=True)
        message="Welcome {}".format(self.cleaned_data["email"])
        admin_message="{0} {1} has just created an account".format(self.cleaned_data['first_name'],self.cleaned_data['last_name'],)
        send_mail(
            "Welcome to Audit Analysis",
            message,
            "site@atech.domain",
            [self.cleaned_data["email"]],
            fail_silently=True
        )
        send_mail("New client has signed up",
            admin_message,
            "site@atech.domain",
            [admin.email],
            fail_silently=True)


class NewClientForm(BSModalForm):
    class Meta:
        model=models.client
        fields=('name','number','users')

class NewEngagementForm(BSModalForm):
    class Meta:
        model=models.engagement
        fields=('name','date')


