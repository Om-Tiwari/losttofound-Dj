# Generated by Django 4.1.4 on 2023-06-29 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_person_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='contact_info',
            field=models.IntegerField(),
        ),
    ]
