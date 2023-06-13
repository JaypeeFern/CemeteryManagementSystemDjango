from django.contrib import admin
from .models import DeceasedInformation, Location

# Register your models here.

class DeceasedAdmin(admin.ModelAdmin):
    list_display = ('id','name','born','died','location' ,'graveimage')
    ordering = ('id','name')
    search_fields = ('id','name')
admin.site.register(DeceasedInformation,DeceasedAdmin)

class LocationAdmin(admin.ModelAdmin):
    list_display = ('id','grave_lot_id','grave_area')
    ordering = ('id',)
    search_fields = ('id',)
admin.site.register(Location,LocationAdmin)

