# Generated by Django 3.0.7 on 2020-07-13 03:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_delete_census'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='DOB',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='participant',
            name='DOH',
            field=models.DateField(blank=True, null=True),
        ),
    ]
