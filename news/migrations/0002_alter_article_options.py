# Generated by Django 4.1 on 2022-08-16 21:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="article",
            options={"ordering": ["-date_created"]},
        ),
    ]
