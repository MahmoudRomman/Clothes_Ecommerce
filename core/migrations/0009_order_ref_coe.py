# Generated by Django 4.1.4 on 2023-08-25 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_order_being_delivered_order_recived_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='ref_coe',
            field=models.CharField(default='123', max_length=20),
            preserve_default=False,
        ),
    ]
