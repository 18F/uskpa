# Generated by Django 2.0.5 on 2018-05-15 15:15

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kpc', '0020_auto_20180514_2237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certificate',
            name='carat_weight',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00899999999999999931998839741709161899052560329437255859375'), message='Carat weight must be at least 0.01')]),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='date_of_shipment',
            field=models.DateField(blank=True, help_text='Date certificate was marked SHIPPED', null=True),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='shipped_value',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Value in USD', max_digits=20, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00899999999999999931998839741709161899052560329437255859375'), message='Shipped value must be greater than 0')]),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='status',
            field=models.IntegerField(choices=[(0, 'Available'), (1, 'Prepared'), (2, 'Shipped'), (3, 'Delivered'), (4, 'Void')], default=0),
        ),
        migrations.AlterField(
            model_name='historicalcertificate',
            name='carat_weight',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00899999999999999931998839741709161899052560329437255859375'), message='Carat weight must be at least 0.01')]),
        ),
        migrations.AlterField(
            model_name='historicalcertificate',
            name='date_of_shipment',
            field=models.DateField(blank=True, help_text='Date certificate was marked SHIPPED', null=True),
        ),
        migrations.AlterField(
            model_name='historicalcertificate',
            name='shipped_value',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Value in USD', max_digits=20, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00899999999999999931998839741709161899052560329437255859375'), message='Shipped value must be greater than 0')]),
        ),
        migrations.AlterField(
            model_name='historicalcertificate',
            name='status',
            field=models.IntegerField(choices=[(0, 'Available'), (1, 'Prepared'), (2, 'Shipped'), (3, 'Delivered'), (4, 'Void')], default=0),
        ),
    ]