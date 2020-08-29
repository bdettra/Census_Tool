from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Count
from django_random_queryset import RandomManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self,email,password,**extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email=self.normalize_email(email)
        user=self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self.db)

    def create_user(self,email,password=None,**extra_fields):
        extra_fields.setdefault("is_staff",False)
        extra_fields.setdefault("is_superuser",False)
        return self._create_user(email,password,**extra_fields)

    def create_superuser(self,email,password,**extra_fields):
        extra_fields.setdefault("is_staff",True)
        extra_fields.setdefault("is_superuser",True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser = True")
        
        return self._create_user(email,password,**extra_fields)

class User(AbstractUser):
    username=None
    email=models.EmailField('email address',unique=True)

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]

    objects=UserManager()

class client(models.Model):
    name=models.CharField(max_length=75)
    number=models.FloatField()
    users=models.ManyToManyField(User)
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
        ("Employee is ineligible and is participating","Employee is ineligible and is participating")
    )
    error_message=models.CharField(choices=CHOICES,max_length=100,null=True)
    participant=models.ForeignKey(participant,on_delete=models.CASCADE)

    '''
    first_name=models.BooleanField(blank=True,null=True)
    last_name=models.BooleanField(blank=True,null=True)
    SSN=models.BooleanField(blank=True,null=True)
    DOB=models.BooleanField(blank=True,null=True)
    DOH=models.BooleanField(blank=True,null=True)
    DOT=models.BooleanField(blank=True,null=True)
    DORH=models.BooleanField(blank=True,null=True)
    hours_worked=models.BooleanField(blank=True,null=True)
    deferral=models.BooleanField(blank=True,null=True)
    catch_up=models.BooleanField(blank=True,null=True)
    eligible=models.BooleanField(blank=True,null=True)
    participating=models.BooleanField(blank=True,null=True)
    contributing=models.BooleanField(blank=True,null=True)
    participant=models.ForeignKey(participant,on_delete=models.CASCADE)
    '''


#class comparison_error(models.Model):


    #first_name=models.BooleanField(blank=True,null=True)
    #last_name=models.BooleanField(blank=True,null=True)
    #SSN=models.BooleanField(blank=True,null=True)
    #DOB=models.BooleanField(blank=True,null=True)
    #DOH=models.BooleanField(blank=True,null=True)
    #DOT=models.BooleanField(blank=True,null=True)
    #DORH=models.BooleanField(blank=True,null=True)
    #participant=models.ForeignKey(participant,on_delete=models.CASCADE)




    















