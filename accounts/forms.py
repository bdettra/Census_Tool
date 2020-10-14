from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from allauth.account.forms import LoginForm, SignupForm
from allauth.utils import set_form_field_order 
from django.conf import settings
from allauth.account.app_settings import AuthenticationMethod



class MyCustomLoginForm(LoginForm):
    """Authentication form which uses boostrap CSS."""

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(MyCustomLoginForm, self).__init__(*args, **kwargs)

        self.fields['login'].widget = forms.TextInput(
                attrs={
                    "type": "email",
                    "placeholder": ("E-mail address"),
                    "autofocus": "autofocus",
                    "class":"form-control",
                }
            )
        
        self.fields['password'].widget = forms.TextInput(
                attrs={
                    "type": "password",
                    "placeholder": ("Password"),
                    "autofocus": "autofocus",
                    "class":"form-control",
                }
            )


class MyCustomSignUpForm(SignupForm):

    first_name=forms.CharField(widget=forms.TextInput({
        'class':'form-control','placeholder':'First Name'
    }))

    last_name=forms.CharField(widget=forms.TextInput({
        'class':'form-control','placeholder':'Last Name'
     }))
    
    def __init__(self,*args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(MyCustomSignUpForm, self).__init__(*args, **kwargs)

        self.fields['email'] =  forms.EmailField(label=("Email"),
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder':'E-Mail Address'}))
        
        self.fields['password1'] =  forms.CharField(label=("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))
                                   
        self.fields['password2'] =  forms.CharField(label=("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Re-Type Password'}))
        

                                   
    '''
    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user   
    '''    




class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = get_user_model()
        fields = ('first_name','last_name','email',)


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = get_user_model()
        fields = ('email',)