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

'''class AuthenticationForm(forms.Form):
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
            fail_silently=True)'''


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

        #Checking to make sure that the client name does not already exist in the database
        if models.client.objects.filter(name=name).exists():
            raise forms.ValidationError("This client name already exists")

        #Checking to make sure tha the client number does not already exist in the database
        elif models.client.objects.filter(number=number).exists():
            raise forms.ValidationError("This client number already exists")


        return self.cleaned_data

class EditClientForm(forms.ModelForm):

    def __init__(self,client,*args,**kwargs):
        self.client=client
        super().__init__(*args,**kwargs)

    class Meta:
        model=models.client
        fields=('name','number','users',)
        widgets={'name':forms.fields.TextInput(attrs={'class':'form-control'}),
        'number':forms.fields.TextInput(attrs={'class':'form-control'}),}


    def clean(self):
        
        name=self.cleaned_data.get("name")
        number=self.cleaned_data.get("number")

        #Checking to make sure that the new client name does not already exist in the database
        if models.client.objects.filter(name=name).exists() and self.client.name != name:
            raise forms.ValidationError("This client name already exists")

        #Checking to make sure that the new client number does not already exist in the database
        elif models.client.objects.filter(number=number).exists() and self.client.number != number:
            raise forms.ValidationError("This client number already exists")

        return self.cleaned_data

    def save(self):
        #Getting the new name, number and users from the form.
        name=self.cleaned_data.get("name")
        number=self.cleaned_data.get("number")
        users=self.cleaned_data.get("users")
        slug=slugify(name)

        #Updating the existing client in the database.
        instance=self.client
        instance.name=name
        instance.number=number
        instance.slug=slug
        instance.users.set(users)
        instance.save()
    
class EditClientUserForm(forms.ModelForm):
    def __init__(self,client,*args,**kwargs):
        self.client=client
        super().__init__(*args,**kwargs)

    class Meta:
        model=models.client
        fields=('primary_user',)

    def save(self):
        primary_user = self.cleaned_data.get("primary_user")

        instance=self.client

        instance.primary_user = primary_user

        instance.save()

class NewEngagementForm(forms.ModelForm):

    def __init__(self,client,*args,**kwargs):
        self.client=client
        super().__init__(*args,**kwargs)

    class Meta:
        model=models.engagement
        fields=('name','date','soc_1_reliance',"first_year",'payroll_provider','tpa')
        widgets={
        'name':forms.fields.TextInput(attrs={"placeholder":"Engagement Name",'class':'form-control'}),
        'date':forms.fields.DateInput(attrs={"placeholder":"Engagement Date",'class':'form-control','id':'datepicker'}),
        "first_year":forms.CheckboxInput,
        "soc_1_reliance":forms.CheckboxInput,
        "tpa":forms.fields.Select(attrs={"placeholder":"TPA",'class':'form-control'}),
        "payroll_provider":forms.fields.Select(attrs={"placeholder":"Payroll Provider",'class':'form-control'}),
        }

        
    def clean(self):
        name=self.cleaned_data.get("name")
        date=self.cleaned_data.get("date")
        

        #Making sure that this engagement name does not already exist for the selected client.
        if models.engagement.objects.filter(name=name,client=self.client).exists():
            raise forms.ValidationError("This engagement name already exists")
            

        return self.cleaned_data

        
    def get_user(self):
        return self.user

class EditEngagementForm(forms.ModelForm):

    def __init__(self,engagement,*args,**kwargs):
        self.engagement=engagement
        super().__init__(*args,**kwargs)

    class Meta:
        model=models.engagement
        fields=('name','date','soc_1_reliance','first_year',"tpa","payroll_provider")
        widgets={
        'name':forms.fields.TextInput(attrs={'placeholder':'Engagement Name','class':'form-control'}),
        'date':forms.fields.DateInput(attrs={"placeholder":"Engagement Date",'class':'form-control','id':'datepicker'}),
        "first_year":forms.CheckboxInput,
        'soc_1_reliance':forms.CheckboxInput,
        "tpa":forms.fields.Select(attrs={"placeholder":"TPA",'class':'form-control'}),
        "payroll_provider":forms.fields.Select(attrs={"placeholder":"Payroll Provider",'class':'form-control'}), 
        }


    def clean(self):
        
        name=self.cleaned_data.get("name")
        date=self.cleaned_data.get("date")
        engagement = self.engagement

        client = engagement.client

        #Checking to make sure that the new client name does not already exist in the database
        if models.engagement.objects.filter(name=name,client=client).exists() and self.engagement.name != name:
            raise forms.ValidationError("This engagement name already exists")

        return self.cleaned_data

    def save(self):
        #Getting the new name, number and users from the form.
        name=self.cleaned_data.get("name")
        date=self.cleaned_data.get("date")
        soc_1_reliance=self.cleaned_data.get("soc_1_reliance")
        first_year=self.cleaned_data.get("first_year")
        tpa=self.cleaned_data.get('tpa')
        payroll_provider=self.cleaned_data.get("payroll_provider")
        slug=slugify(name)

        #Updating the existing client in the database.
        instance=self.engagement
        instance.name=name
        instance.date=date
        instance.slug=slug
        instance.soc_1_reliance= soc_1_reliance
        instance.tpa=tpa
        instance.payroll_provider=payroll_provider
        instance.first_year=first_year
        instance.save()

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

        #Getting the age, service hours, service days, service months, service years, excluded employees and entry date data
        #from the form and appending it to the data list.
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

        #Iterating through the data list and perorming data validation on each of the form attributes.
        for value in data:
            if value is None:
                value=0
            if value < 0:
                raise forms.ValidationError("Values must be greater than 0.")

        return self.cleaned_data

    
    def save(self,engagement):
        '''A custom save function for the eligiblity form so that users can either update existing eligiblity rules for an engagement
        or if the engagement is brand new they can create a new set of eligiblity rules'''
        
        data=[]

        #Getting the age, service hours, service days, service months, service years, excluded employees and entry date data
        #from the form and appending it to the data list.
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
        #Iterating through the data list and perorming data validation on each of the form attributes.
        for value in data:
            print(value)
        for value in range(len(data)):
            if data[value] is None:
                data[value]=int(0)
                
        
        #Either finding the existing eligiblity rules object in the database or creating a new eligilbity rules object in the database.
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

class NewClientContact(forms.ModelForm):

    def __init__(self,engagement,*args,**kwargs):
        self.engagement=engagement
        super().__init__(*args,**kwargs)

    class Meta:
        model=models.client_contact
        fields=['first_name','last_name','position','email']
        widgets={'first_name':forms.fields.TextInput(attrs={'placeholder':'First Name','class':'form-control'}),
                'last_name':forms.fields.TextInput(attrs = {'placeholder':'Last Name','class':'form-control'}),
                'position':forms.fields.TextInput(attrs = {'placeholder':'Position','class':'form-control'}),
                'email':forms.fields.TextInput(attrs = {'placeholder':'Email Address','class':'form-control'})}

    def save(self):
        first_name = self.cleaned_data.get("first_name")
        last_name = self.cleaned_data.get("last_name")
        position = self.cleaned_data.get("position")
        email = self.cleaned_data.get("email")
        engagement=self.engagement

        instance = models.client_contact.objects.create(first_name=first_name,last_name=last_name,position=position,email=email,engagement=engagement)
        instance.save()




class EditSelection(forms.ModelForm):
    class Meta:
        model=models.participant
        fields=['selection']
        widgets={'selection':forms.CheckboxInput}

    def clean(self):
        selection = self.cleaned_data.get("selection")

        if selection is None:
            selection = False
        
        return self.cleaned_data

class ErrorForm(forms.ModelForm):
    class Meta:
        model=models.error
        fields=['error_message']
        widgets={"error_message":forms.HiddenInput()}

class ContactDeleteForm(forms.ModelForm):
    class Meta:
        model=models.client_contact
        fields=['first_name']
        widgets={"first_name":forms.HiddenInput()}
    


    
    



