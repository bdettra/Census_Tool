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
import pandas as pd
from django.utils.text import slugify

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
    class Meta(DjangoUserCreationForm.Meta):
        model=models.User
        fields=('first_name','last_name','email')
        field_classes={"email":UsernameField}
        widgets={'company_name':forms.fields.TextInput(attrs={"placeholder":"Company Name",'class':'form-control'}),
        'first_name':forms.fields.TextInput(attrs={"placeholder":"First Name",'class':'form-control'}),
        'last_name':forms.fields.TextInput(attrs={"placeholder":"Last Name",'class':'form-control'}),
        "email":forms.fields.TextInput(attrs={"placeholder":"Email",'class':'form-control'}),
        "password1":forms.fields.TextInput(attrs={"placeholder":"Password"}),
        "passwrod2":forms.fields.TextInput(attrs={"placeholder":"Re-type Password"})}


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


class NewClientForm(forms.ModelForm):
    error_css_class = 'error'
    class Meta:
        model=models.client
        fields=('name','number','users')
        widgets={'name':forms.fields.TextInput(attrs={"placeholder":"Client Name",'class':'form-control','error_class':'is_invalid'}),
        'number':forms.fields.TextInput(attrs={"placeholder":"Client Number",'class':'form-control'})}


    def clean(self):
        name=self.cleaned_data.get("name")
        number=self.cleaned_data.get("number")

        if models.client.objects.filter(name=name).exists():
            raise forms.ValidationError("This client name already exists")

        elif models.client.objects.filter(number=number).exists():
            raise forms.ValidationError("This client number already exists")


        return self.cleaned_data

class EditClientForm(forms.ModelForm):

    def __init__(self,client,*args,**kwargs):
        self.client=client
        super().__init__(*args,**kwargs)

    class Meta:
        model=models.client
        fields=('name','number','users')
        widgets={'name':forms.fields.TextInput(attrs={'class':'form-control'}),
        'number':forms.fields.TextInput(attrs={'class':'form-control'})}


    def clean(self):
        name=self.cleaned_data.get("name")
        number=self.cleaned_data.get("number")

        if models.client.objects.filter(name=name).exists() and self.client.name != name:
            raise forms.ValidationError("This client name already exists")

        elif models.client.objects.filter(number=number).exists() and self.client.number != number:
            raise forms.ValidationError("This client number already exists")

        return self.cleaned_data

    def save(self):
        name=self.cleaned_data.get("name")
        number=self.cleaned_data.get("number")
        users=self.cleaned_data.get("users")
        slug=slugify(name)
        instance=self.client
        instance.name=name
        instance.number=number
        instance.slug=slug
        instance.users.set(users)
        instance.save()




class NewEngagementForm(BSModalForm):

    def __init__(self,client,*args,**kwargs):
        self.client=client
        super().__init__(*args,**kwargs)

    class Meta:
        model=models.engagement
        fields=('name','date')
        widgets={'name':forms.fields.TextInput(attrs={"placeholder":"Engagement Name",'class':'form-control'}),
        'date':forms.fields.TextInput(attrs={"placeholder":"Engagement Date",'class':'form-control'})}

        
    def clean(self):
        name=self.cleaned_data.get("name")
        date=self.cleaned_data.get("date")

        if models.engagement.objects.filter(name=name,client=self.client).exists():
            raise forms.ValidationError("This engagement name already exists")
            

        return self.cleaned_data

        
    def get_user(self):
        return self.user

class EligibilityForm(forms.ModelForm):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    class Meta:
        model=models.eligibility_rules
        fields=("age","service_hours","service_days","service_months","service_years",
        "excluded_employees","entry_date",)

        widgets={'age':forms.fields.NumberInput(attrs={"placeholder":"Enter Age",'class':'form-control'}),
        'service_hours':forms.fields.NumberInput(attrs={"placeholder":"Enter Service Hours",'class':'form-control'}),
        'service_days':forms.fields.NumberInput(attrs={"placeholder":"Enter Service Days",'class':'form-control'}),
        'service_months':forms.fields.NumberInput(attrs={"placeholder":"Enter Service Months",'class':'form-control'}),
        'service_years':forms.fields.NumberInput(attrs={"placeholder":"Enter Service Years",'class':'form-control'}),
        'excluded_employees':forms.Textarea(attrs={"rows":3,"placeholder":"Enter Excluded Employees",'class':'form-control'}),
        'entry_date':forms.fields.Select(attrs={"placeholder":"Enter Entry Date",'class':'form-control'})
        }

    def clean(self):
        data=[]
        age=self.cleaned_data.get("age")
        data.append(age)

        service_hours=self.cleaned_data.get("service_hours")
        data.append(service_hours)

        service_days=self.cleaned_data.get("service_days")
        data.append(service_days)

        service_months=self.cleaned_data.get("service_months")
        data.append(service_months)

        service_years=self.cleaned_data.get("service_years")
        data.append(service_years)
        
        excluded_employees=self.cleaned_data.get("excluded_employees")

        entry_date=self.cleaned_data.get("entry_date")

        for value in data:
            if value is None:
                value=0
            if value < 0:
                raise forms.ValidationError("Values must be greater than 0.")

        return self.cleaned_data

    
    def save(self,engagement):
        data=[]
        age=self.cleaned_data.get("age")
        data.append(age)

        service_hours=self.cleaned_data.get("service_hours")
        data.append(service_hours)

        service_days=self.cleaned_data.get("service_days")
        data.append(service_days)

        service_months=self.cleaned_data.get("service_months")
        data.append(service_months)

        service_years=self.cleaned_data.get("service_years")
        data.append(service_years)
        
        excluded_employees=self.cleaned_data.get("excluded_employees")

        entry_date=self.cleaned_data.get("entry_date")
        for value in data:
            print(value)
        for value in range(len(data)):
            if data[value] is None:
                data[value]=int(0)
                
        

        eligibility_rules,created=models.eligibility_rules.objects.get_or_create(engagement=engagement)
        eligibility_rules.age=data[0]
        eligibility_rules.service_hours=data[1]
        eligibility_rules.service_days=data[2]
        eligibility_rules.service_months=data[3]
        eligibility_rules.service_years=data[4]
        eligibility_rules.entry_date=entry_date
        eligibility_rules.excluded_employees=excluded_employees
        eligibility_rules.save()
    

class CensusFileForm(forms.Form):
    filename=forms.FileField()

class KeyEmployeeSelectForm(forms.Form):
    employees=forms.ModelMultipleChoiceField(queryset=models.engagement.objects.none(),widget=forms.CheckboxSelectMultiple)

    def __init__(self,engagement,*args,**kwargs):
        super(KeyEmployeeSelectForm,self).__init__(*args,**kwargs)
        self.fields['employees'].queryset = models.participant.objects.filter(engagement=engagement)
        self.__name__="KeyEmployeeSelectForm"

class KeyEmployee(forms.ModelForm):
    class Meta:
        model=models.participant
        fields=['key_employee']
        widgets={'key_employee':forms.CheckboxInput}

    def clean(self):
        key_employee=self.cleaned_data.get("key_employee")

        if key_employee is None:
            key_employee=False

        return self.cleaned_data

class ErrorForm(forms.ModelForm):
    class Meta:
        model=models.error
        fields=['error_message']
        widgets={"error_message":forms.HiddenInput()}
    


    
    



