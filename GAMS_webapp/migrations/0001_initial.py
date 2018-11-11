# Generated by Django 2.1.3 on 2018-11-07 15:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attendance_datetime', models.DateTimeField(blank=True, null=True)),
                ('remarks', models.CharField(blank=True, max_length=50, null=True)),
                ('is_present', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Grades',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instructor', models.CharField(blank=True, max_length=100, null=True)),
                ('equivalent', models.FloatField(blank=True, max_length=10, null=True)),
                ('remarks', models.CharField(blank=True, max_length=50, null=True)),
                ('datetime_created', models.DateTimeField(blank=True, null=True)),
                ('datetime_modified', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ParentMonitor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='SchClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_code', models.CharField(blank=True, max_length=50, null=True)),
                ('course', models.CharField(blank=True, max_length=128, null=True)),
                ('class_year', models.CharField(blank=True, max_length=28, null=True)),
                ('schclass_name', models.CharField(blank=True, max_length=128, null=True)),
                ('section', models.CharField(blank=True, max_length=30, null=True)),
                ('verified', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SchClass_Join_Approval',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verified', models.BooleanField(default=False)),
                ('schclass', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GAMS_webapp.SchClass')),
            ],
        ),
        migrations.CreateModel(
            name='UserExt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('middle_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('user_type', models.CharField(max_length=50)),
                ('is_active', models.BooleanField(blank=True, default=True)),
                ('course', models.CharField(max_length=100, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(blank=True, max_length=165, null=True)),
                ('gender', models.CharField(blank=True, max_length=20, null=True)),
                ('birthday', models.DateField(blank=True, null=True)),
                ('contact_number', models.CharField(blank=True, max_length=50, null=True)),
                ('guardian_contact_number', models.CharField(blank=True, max_length=50, null=True)),
                ('profile_photo', models.ImageField(blank=True, null=True, upload_to='')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GAMS_webapp.UserExt')),
            ],
        ),
        migrations.AddField(
            model_name='schclass_join_approval',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GAMS_webapp.UserExt'),
        ),
        migrations.AddField(
            model_name='schclass',
            name='instructor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GAMS_webapp.UserExt'),
        ),
        migrations.AddField(
            model_name='parentmonitor',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userext1', to='GAMS_webapp.UserExt'),
        ),
        migrations.AddField(
            model_name='parentmonitor',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userext2', to='GAMS_webapp.UserExt'),
        ),
        migrations.AddField(
            model_name='grades',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GAMS_webapp.UserExt'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='schclass',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GAMS_webapp.SchClass'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GAMS_webapp.UserExt'),
        ),
    ]