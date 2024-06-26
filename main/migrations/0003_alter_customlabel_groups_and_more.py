# Generated by Django 4.2.4 on 2024-05-17 04:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('main', '0002_customlabel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customlabel',
            name='groups',
            field=models.ManyToManyField(related_name='customlabel_groups', to='auth.group'),
        ),
        migrations.AlterField(
            model_name='customlabel',
            name='user_permissions',
            field=models.ManyToManyField(related_name='customlabel_permissions', to='auth.permission'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='groups',
            field=models.ManyToManyField(related_name='customuser_groups', to='auth.group'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='user_permissions',
            field=models.ManyToManyField(related_name='customuser_permissions', to='auth.permission'),
        ),
    ]
