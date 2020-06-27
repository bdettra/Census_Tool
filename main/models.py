from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Count


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
    company_name=models.CharField(max_length=100,verbose_name="Company Name: ")

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

class TemplateSpreadsheet(models.Model):
    name=models.CharField(max_length=50)
    client=models.ForeignKey(client,on_delete=models.CASCADE)

class spreadsheet(models.Model):
    name=models.CharField(max_length=100,verbose_name="Spreadsheet Name: ")
    template=models.ForeignKey(TemplateSpreadsheet,on_delete=models.CASCADE)
    date=models.DateField()

class column(models.Model):
    CHOICES=(
        ("String","String"),
        ('Float',"Float"),
        ("Date","Date"),
        ("Integer","Integer"),
    )
    name=models.CharField(max_length=25)
    spreadsheet=models.ManyToManyField(spreadsheet)
    d_type=models.CharField(choices=CHOICES,max_length=25)

class StringRow(models.Model):
    column=models.ForeignKey(column,on_delete=models.CASCADE)
    data=models.CharField(max_length=50)

class FloatRow(models.Model):
    column=models.ForeignKey(column,on_delete=models.CASCADE)
    data=models.FloatField()

class IntegerRow(models.Model):
    column=models.ForeignKey(column,on_delete=models.CASCADE)
    data=models.IntegerField()

class DateRow(models.Model):
    column=models.ForeignKey(column,on_delete=models.CASCADE)
    data=models.DateField


    















