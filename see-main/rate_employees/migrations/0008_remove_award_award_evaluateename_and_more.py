# Generated by Django 5.0.6 on 2024-06-23 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rate_employees', '0007_award_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='award',
            name='award_evaluateename',
        ),
        migrations.RemoveField(
            model_name='award',
            name='award_evaluatorname',
        ),
        migrations.AddField(
            model_name='award',
            name='award_evaluateeid',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='award',
            name='award_evaluatorid',
            field=models.IntegerField(default=0),
        ),
    ]
