# Generated by Django 5.0.6 on 2024-07-01 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rate_employees', '0011_award_remark'),
    ]

    operations = [
        migrations.AlterField(
            model_name='award',
            name='remark',
            field=models.CharField(default=' ', max_length=50),
        ),
    ]
