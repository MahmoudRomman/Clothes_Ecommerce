# Generated by Django 4.2.5 on 2023-09-18 13:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_remove_order_refund_granted_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='being_delivered',
        ),
        migrations.RemoveField(
            model_name='order',
            name='recived',
        ),
    ]
