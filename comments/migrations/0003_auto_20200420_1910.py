# Generated by Django 3.0.4 on 2020-04-20 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0002_auto_20200416_0937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='ipaddress',
            field=models.GenericIPAddressField(null=True),
        ),
    ]