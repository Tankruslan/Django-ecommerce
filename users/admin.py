from django.contrib import admin
from .models import *

# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
	list_display_links = [field.name for field in Profile._meta.fields]
	list_display = [field.name for field in Profile._meta.fields]
	class Meta:
		model = Profile
# Register your models here.
admin.site.register(Profile, ProfileAdmin)