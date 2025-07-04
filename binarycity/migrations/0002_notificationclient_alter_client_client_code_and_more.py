# Generated by Django 4.2.19 on 2025-07-04 10:54

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('binarycity', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationClient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('phone_number', models.CharField(db_index=True, max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AlterField(
            model_name='client',
            name='client_code',
            field=models.CharField(blank=True, db_index=True, max_length=6, unique=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='name',
            field=models.CharField(db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='contact',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.EmailField(db_index=True, max_length=254, unique=True, validators=[django.core.validators.EmailValidator()]),
        ),
        migrations.AlterField(
            model_name='contact',
            name='name',
            field=models.CharField(db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='contact',
            name='surname',
            field=models.CharField(db_index=True, max_length=255),
        ),
        migrations.AddIndex(
            model_name='client',
            index=models.Index(fields=['name', 'client_code'], name='binarycity__name_1c3deb_idx'),
        ),
        migrations.AddIndex(
            model_name='client',
            index=models.Index(fields=['created_at'], name='binarycity__created_1d5181_idx'),
        ),
        migrations.AddIndex(
            model_name='contact',
            index=models.Index(fields=['surname', 'name'], name='binarycity__surname_7288e8_idx'),
        ),
        migrations.AddIndex(
            model_name='contact',
            index=models.Index(fields=['email'], name='binarycity__email_91cc74_idx'),
        ),
        migrations.AddIndex(
            model_name='contact',
            index=models.Index(fields=['created_at'], name='binarycity__created_681326_idx'),
        ),
        migrations.AddIndex(
            model_name='notificationclient',
            index=models.Index(fields=['name'], name='binarycity__name_d20800_idx'),
        ),
        migrations.AddIndex(
            model_name='notificationclient',
            index=models.Index(fields=['phone_number'], name='binarycity__phone_n_6de157_idx'),
        ),
    ]
