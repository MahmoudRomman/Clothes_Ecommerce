# Generated by Django 4.2.5 on 2023-09-18 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_remove_order_being_delivered_remove_order_recived'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='refund_accepted',
            field=models.BooleanField(default=False),
        ),
    ]
