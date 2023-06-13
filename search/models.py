from enum import auto
from django.db import models
import secrets
import string

# Create your models here.

class Location(models.Model):
    date_created = models.DateTimeField(auto_now=True)
    grave_lot_id = models.CharField(max_length=2)
    grave_area = models.CharField(max_length=64)
    
    def get_grave_lot_id(self):
        return {self.grave_lot_id}
    
    def get_grave_area(self):
        return {self.grave_area}
    
    def __str__(self):
        return f"{self.grave_area}"
    
    def save(self, *args, **kwargs):
        for field_name in ['grave_area']:
            val = getattr(self, field_name, False)
            if val:
                setattr(self, field_name, val.upper())
        super(Location, self).save(*args, **kwargs)
    
def randomGenerator():
    alphabet = string.ascii_letters
    random = ''.join(secrets.choice(alphabet) for i in range(10))
    return random
    
class DeceasedInformation(models.Model):
    date_created = models.DateTimeField(auto_now=True)
    reference_number = models.CharField(max_length=10, editable=True, default=randomGenerator)
    name = models.CharField(max_length=64)
    born = models.DateField(blank=True)
    died = models.DateField(blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="gravelocation")
    graveimage = models.ImageField(null=True, blank=True, upload_to="Images/")
     
    def get_grave_lot_id(self):
        return f"{self.location.grave_lot_id}"
    
    def get_grave_area(self):
        return f"{self.location.grave_area}"
        
    
    def __str__(self):
        return f"{self.id}: {self.name}, {self.born}, {self.died}, {self.location}, {self.graveimage}"
