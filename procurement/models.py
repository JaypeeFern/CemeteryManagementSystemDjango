from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from search.models import Location
import random
from datetime import datetime

# Create your models here.

class LotType(models.Model):
    date_created = models.DateTimeField(auto_now=True)
    Lot_Photo = models.ImageField(upload_to='lot_photo', blank=True, null=True)
    Lot_Name = models.CharField(max_length=64)
    Lot_Descriptions = models.TextField(max_length=500, blank=True)
    # Lot_Capacity = models.IntegerField()
    
    def __str__(self):
        return f'{self.Lot_Name}'

class GardenDetail(models.Model):
    date_created = models.DateTimeField(auto_now=True)
    Lot_Image = models.ImageField(null=True, blank=True, upload_to="Images/")
    Garden_Name = models.ForeignKey(Location, on_delete=models.CASCADE, max_length=64, null=True, related_name="gardenname")
    Garden_Description = models.TextField(max_length=255, null=True, blank=True)
    Available_Space = models.IntegerField(blank=True, default=0)
    Date_Modified = models.DateTimeField(auto_now=True)
    Lot_Type = models.ManyToManyField(LotType)
    
    # def save(self, *args, **kwargs):
    #     self.Available_Space = LotType.objects.aggregate(Lot_Capacity=Sum('Lot_Capacity'))['Lot_Capacity']
    #     super(GardenDetail, self).save(*args, **kwargs) # Call the "real" save() method.
    
    def get_Lot_Type(self):
        return f'{self.Lot_Type.Lot_Name}'

    def __str__(self):
        return f'{self.Garden_Name}'
    
CUSTOMER_STATUS = (
    (True, 'Processed'),
    (False, 'Not Processed')
)

def ref():
    current_year = datetime.now().year 
    numbers = random.randrange(0,100,4)
    result = ''.join(f"SMPI-{current_year}-{numbers}")
    return result

class Customer(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=20, editable=False, default=ref)
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    first_Name = models.CharField(max_length=64, null=True)
    last_Name = models.CharField(max_length=64, null=True)
    contact_Number = models.CharField(max_length=64, null=True)
    deceased_Name = models.CharField(max_length=64, null=True)
    born_Date = models.DateField(null=True)
    died_Date = models.DateField(null=True)
    burial_Schedule = models.DateField(null=True)
    chosen_Lot = models.ForeignKey(GardenDetail, on_delete=models.CASCADE, null=True, related_name="chosenLot")
    chosen_Lot_Type = models.ForeignKey(LotType, on_delete=models.CASCADE, null=True, related_name="chosenLotType")
    status = models.BooleanField(choices=CUSTOMER_STATUS, default=False)
    
    def get_lot_number(self):
        return f'{self.chosen_Lot.Garden_Name.grave_lot_id}'
    
    def get_lot_name(self):
        return f'{self.chosen_Lot.Garden_Name.grave_area}'
    
    def __str__(self):
        return f'{self.submitted_by}, {self.first_Name}, {self.last_Name}, {self.contact_Number}, {self.deceased_Name}, {self.born_Date}, {self.died_Date}, {self.burial_Schedule}, {self.chosen_Lot}, {self.chosen_Lot_Type}, {self.status}'
    