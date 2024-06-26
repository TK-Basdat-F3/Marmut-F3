# Generated by Django 4.2.4 on 2024-05-17 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('main', '0003_alter_customlabel_groups_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customlabel',
            name='groups',
            field=models.ManyToManyField(related_name='custom_label_groups', to='auth.group'),
        ),
        migrations.AlterField(
            model_name='customlabel',
            name='user_permissions',
            field=models.ManyToManyField(related_name='custom_label_permissions', to='auth.permission'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='groups',
            field=models.ManyToManyField(related_name='custom_user_groups', to='auth.group'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='user_permissions',
            field=models.ManyToManyField(related_name='custom_user_permissions', to='auth.permission'),
        ),
    ]
