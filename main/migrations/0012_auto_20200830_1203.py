# Generated by Django 3.0.7 on 2020-08-30 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_auto_20200830_1111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='error',
            name='error_message',
            field=models.CharField(choices=[('First name data is missing', 'First name data is missing'), ('First name data does not match previous year census', 'First name data does not match previous year census'), ('Last name data is missing', 'Last name data is missing'), ('Last name data does not match previous year census', 'Last name data does not match previous year census'), ('Social Security Number data is missing', 'Social Security Number data is missing'), ('DOB data is missing', 'DOB data is missing'), ('DOB data does not match previous year census', 'DOB data does not match previous year census'), ('DOH data is missing', 'DOH data is missing'), ('DOH data does not match previous year census', 'DOH data does not match previous year census'), ('DOT is before engagement year', 'DOT is before engagement year'), ('DOT data does not match previous year census', 'DOT data does not match previous year census'), ('DORH data does not match previous year census', 'DORH data does not match previous year census'), ('Hours worked data is missing', 'Hours worked data is missing'), ('Contribution amount is over IRS limit', 'Contribution amount is over IRS limit'), ('Catch-up contribution amount is over IRS limit', 'Catch-up contribution amount is over IRS limit'), ('Employee is ineligible and is participating', 'Employee is ineligible and is participating'), ('Eligible wages are greater than IRS limit', 'Eligible wages are greater than IRS limit'), ('Employee contributions are greater than IRS limit', 'Employee contributions are greater than IRS limit'), ('Catch-up contributions are greater than IRS limit', 'Catch-up contributions are greater than IRS limit'), ('Employee is not eligible for catch-up contributions', 'Employee is not eligible for catch-up contributions'), ('Employee is excluded but is participating', 'Employee is excluded but is particiapting')], max_length=100, null=True),
        ),
    ]
