from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class UserExt(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    user_type = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True, blank=True)
    course = models.CharField(max_length=100, null=True)


class UserProfile(models.Model):
    user = models.ForeignKey(UserExt, on_delete=models.CASCADE)
    address = models.CharField(max_length=165, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    birthday = models.DateField(null=True, blank=True)
    contact_number = models.CharField(max_length=50, blank=True, null=True)
    guardian_contact_number = models.CharField(max_length=50, blank=True, null=True)
    profile_photo = models.ImageField(blank=True, null=True)


class SchClass(models.Model):
    class_code = models.CharField(max_length=50, blank=True, null=True)
    course = models.CharField(max_length=128, blank=True, null=True)
    class_year = models.CharField(max_length=28, blank=True, null=True)
    schclass_name = models.CharField(max_length=128, blank=True, null=True)
    instructor = models.ForeignKey(UserExt, on_delete=models.CASCADE)
    section = models.CharField(max_length=30, blank=True, null=True)
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(blank=True, null=True)


class Grades(models.Model):
    schclass = models.ForeignKey(SchClass, on_delete=models.CASCADE, related_name='schclass')
    student = models.ForeignKey(UserExt, on_delete=models.CASCADE, related_name='student')
    instructor = models.ForeignKey(UserExt, on_delete=models.CASCADE, related_name='instructor')
    equivalent = models.FloatField(max_length=10, null=True, blank=True)
    remarks = models.CharField(max_length=50, blank=True, null=True)
    datetime_modified = models.DateTimeField(blank=True, null=True)


class Attendance(models.Model):
    schclass = models.ForeignKey(SchClass, on_delete=models.CASCADE)
    student = models.ForeignKey(UserExt, on_delete=models.CASCADE)
    attendance_datetime = models.DateTimeField(blank=True, null=True)
    remarks = models.CharField(max_length=50, null=True, blank=True)
    is_present = models.BooleanField(default=False)


class SchClass_Join_Approval(models.Model):
    schclass = models.ForeignKey(SchClass, on_delete=models.CASCADE)
    student = models.ForeignKey(UserExt, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)


class ParentMonitor(models.Model):
    schclass = models.ForeignKey(SchClass, on_delete=models.CASCADE, related_name='schclass_parent_monitor')
    parent = models.ForeignKey(UserExt, on_delete=models.CASCADE, related_name='userext1')
    student = models.ForeignKey(UserExt, on_delete=models.CASCADE, related_name='userext2')
    verified = models.BooleanField(default=False)
