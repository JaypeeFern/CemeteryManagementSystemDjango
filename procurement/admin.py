from django.contrib import admin
from .models import GardenDetail, LotType, Customer

# Register your models here.

class GardenDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'Lot_Image', 'Garden_Name', 'Garden_Description','Available_Space', 'Date_Modified')
    filter_horizontal = ('Lot_Type',)
admin.site.register(GardenDetail, GardenDetailsAdmin)

class LotTypesAdmin(admin.ModelAdmin):
    list_display = ('Lot_Name', 'Lot_Descriptions')
admin.site.register(LotType, LotTypesAdmin)

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'first_Name', 'last_Name', 'contact_Number', 'status')
    ordering = ('first_Name',)
    search_fields = ('first_Name',)
    list_filter = ('chosen_Lot','chosen_Lot_Type','status')
    # exclude = ('submitted_by',)
admin.site.register(Customer, CustomerAdmin)
