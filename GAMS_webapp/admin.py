from django.contrib import admin
from . models import UserExt, UserProfile, SchClass, Attendance,\
     SchClass_Join_Approval, ParentMonitor

admin.site.site_header = 'Academia Administration'

# Register your models here.
admin.site.register(UserExt)
admin.site.register(UserProfile)
admin.site.register(SchClass)
admin.site.register(Attendance)
admin.site.register(SchClass_Join_Approval)
admin.site.register(ParentMonitor)
