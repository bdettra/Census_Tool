from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Count
from django_random_queryset import RandomManager
from django.contrib.auth import get_user_model


class client(models.Model):
    name=models.CharField(max_length=75)
    number=models.FloatField()
    users=models.ManyToManyField(get_user_model())
    slug=models.SlugField()

class engagement(models.Model):
    name=models.CharField(max_length=50,verbose_name="Engagement Name: ")
    date=models.DateField()
    client=models.ForeignKey(client,on_delete=models.CASCADE)
    slug=models.SlugField()
    soc_1_reliance=models.BooleanField(default=False)

class eligibility_rules(models.Model):
    CHOICES=(
        ("Immediately","Immediately"),
        ("First day of following Month", "First day of following month"),
        ("Semi Annual (Jan 1 or July 1)", "Semi Annual (Jan 1 or July 1)"),
        ("Annual (Jan 1)","Annual (Jan 1)"),
    )

    age=models.IntegerField(null=True,blank=True)
    service_hours=models.IntegerField(null=True,blank=True)
    service_days=models.IntegerField(null=True, blank=True)
    service_months=models.IntegerField(null=True,blank=True)
    service_years=models.IntegerField(null=True,blank=True)
    excluded_employees=models.TextField(blank=True, null=True)
    entry_date=models.CharField(choices=CHOICES,max_length=50,default="Immediately")
    engagement=models.ForeignKey(engagement,on_delete=models.CASCADE)
    

class participant(models.Model):
    objects=RandomManager()

    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    SSN=models.CharField(max_length=11)
    DOB=models.DateField(blank=True, null=True)
    DOH=models.DateField(blank=True, null=True)
    DOT=models.DateField(blank=True, null=True)
    DORH=models.DateField(blank=True,null=True)
    excluded=models.BooleanField(blank=True,null=True)
    gross_wages=models.FloatField(blank=True,null=True,validators=[MinValueValidator(0)])
    eligible_wages=models.FloatField(blank=True,null=True,validators=[MinValueValidator(0)])
    hours_worked=models.FloatField(blank=True,null=True,validators=[MinValueValidator(0)])
    EE_pre_tax_amount=models.FloatField(blank=True,null=True,validators=[MinValueValidator(0)])
    ER_pre_tax_amount=models.FloatField(blank=True,null=True,validators=[MinValueValidator(0)])
    EE_roth_amount=models.FloatField(blank=True,null=True,validators=[MinValueValidator(0)])
    ER_roth_amount=models.FloatField(blank=True,null=True,validators=[MinValueValidator(0)])
    EE_catch_up=models.FloatField(blank=True,null=True,validators=[MinValueValidator(0)])
    ER_catch_up=models.FloatField(blank=True,null=True,validators=[MinValueValidator(0)])
    total_EE_deferral=models.FloatField(blank=True,null=True,validators=[MinValueValidator(0)])
    total_ER_deferral=models.FloatField(blank=True,null=True,validators=[MinValueValidator(0)])
    effective_deferral_percentage=models.FloatField(blank=True,null=True)
    selection=models.BooleanField(blank=True,null=True)
    key_employee=models.BooleanField(blank=True,null=True)
    eligible=models.BooleanField(blank=True,null=True)
    participating=models.BooleanField(blank=True,null=True)
    contributing=models.BooleanField(blank=True,null=True)
    engagement=models.ForeignKey(engagement,on_delete=models.CASCADE)


    def __str__(self):
        return self.first_name +" "+ self.last_name

class error(models.Model):
    CHOICES=(
        ("First name data is missing","First name data is missing"),
        ("First name data does not match previous year census","First name data does not match previous year census"),
        ("Last name data is missing","Last name data is missing"),
        ("Last name data does not match previous year census","Last name data does not match previous year census"),
        ("Social Security Number data is missing","Social Security Number data is missing"),
        ("DOB data is missing","DOB data is missing"),
        ("DOB data does not match previous year census","DOB data does not match previous year census"),
        ("DOH data is missing","DOH data is missing"),
        ("DOH data does not match previous year census","DOH data does not match previous year census"),
        ("DOT is before engagement year","DOT is before engagement year"),
        ("DOT data does not match previous year census","DOT data does not match previous year census"),
        ("DORH data does not match previous year census","DORH data does not match previous year census"),
        ("Hours worked data is missing","Hours worked data is missing"),
        ("Contribution amount is over IRS limit","Contribution amount is over IRS limit"),
        ("Catch-up contribution amount is over IRS limit","Catch-up contribution amount is over IRS limit"),
        ("Employee is ineligible and is participating","Employee is ineligible and is participating"),
        ("Eligible wages are greater than IRS limit","Eligible wages are greater than IRS limit"),
        ("Employee contributions are greater than IRS limit","Employee contributions are greater than IRS limit"),
        ("Employee is not eligible for catch-up contributions","Employee is not eligible for catch-up contributions"),
        ("Employee is not eligible for catch-up contributions (No catch-up column)","Employee is not eligible for catch-up contributions (No catch-up column)"),
        ("Employee is excluded but is participating","Employee is excluded but is particiapting"),
    )
    error_message=models.CharField(choices=CHOICES,max_length=100,null=True)
    participant=models.ForeignKey(participant,on_delete=models.CASCADE)

    def __str__(self):
        return self.error_message
    






    















