# Generated by Django 5.2.1 on 2025-06-02 18:53

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='description',
        ),
        migrations.AddField(
            model_name='cartitem',
            name='portions',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='portions',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='deliverytype',
            name='name',
            field=models.CharField(choices=[('regular', 'Regular'), ('express', 'Express')], default='regular', max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='deliverytype',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='giftdetails',
            name='recipient_matric_number',
            field=models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(message='Matric number must contain only numbers', regex='^\\d+$')]),
        ),
        migrations.AlterField(
            model_name='giftdetails',
            name='whatsapp_number',
            field=models.CharField(max_length=11, validators=[django.core.validators.RegexValidator(message='WhatsApp number must be exactly 11 digits and start with 0', regex='^0\\d{10}$')]),
        ),
        migrations.AlterField(
            model_name='location',
            name='name',
            field=models.CharField(choices=[('hall1', 'Hall 1'), ('hall2', 'Hall 2'), ('hall3', 'Hall 3'), ('faculty_sci', 'Faculty of Science'), ('faculty_eng', 'Faculty of Engineering'), ('faculty_arts', 'Faculty of Arts'), ('library', 'University Library'), ('cafe', 'University Cafeteria')], default='hall1', max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='api.deliverytype'),
        ),
        migrations.AlterField(
            model_name='order',
            name='location',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='api.location'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('preparing', 'Preparing'), ('ready', 'Ready'), ('delivering', 'Delivering'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='plates',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
