# Generated by Django 4.0.4 on 2023-03-22 00:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdfreaderApp', '0006_invoices_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoices',
            name='code',
            field=models.CharField(default='847cf65226-2B044', max_length=50, unique=True),
        ),
    ]
