# Generated by Django 2.2.7 on 2019-12-03 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Frients', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='describe',
            field=models.CharField(default=True, max_length=1000),
        ),
    ]
