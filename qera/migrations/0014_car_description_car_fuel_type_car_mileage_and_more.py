# Generated by Django 5.1.2 on 2024-11-23 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qera', '0013_remove_car_image_carimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='description',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='car',
            name='fuel_type',
            field=models.CharField(choices=[('Petrol', 'Petrol'), ('Diesel', 'Diesel'), ('Electric', 'Electric')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='car',
            name='mileage',
            field=models.DecimalField(decimal_places=2, help_text='Mileage in km/l or equivalent', max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='car',
            name='seating_capacity',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='car',
            name='transmission_type',
            field=models.CharField(choices=[('Manual', 'Manual'), ('Automatic', 'Automatic')], max_length=50, null=True),
        ),
    ]
