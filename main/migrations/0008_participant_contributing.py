# Generated by Django 3.0.7 on 2020-07-26 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_remove_user_company_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='contributing',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
