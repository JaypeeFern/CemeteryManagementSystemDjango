from django import forms
from search.models import DeceasedInformation, Location
from procurement.models import LotType, GardenDetail, Customer
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from bootstrap_modal_forms.forms import BSModalModelForm

# ---------------------------------------------------------------------------- #
#                             Deceased Information                             #
# ---------------------------------------------------------------------------- #

class DeceasedInfoForm(BSModalModelForm):
    class Meta:
        model = DeceasedInformation
        fields = ('__all__')
        exclude = ('reference_number',)
        widgets = {
            'name': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': '#'}),
            'born': forms.TextInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': '#'}),
            'died': forms.TextInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': '#'}),
            'location': forms.Select(attrs={'class': 'form-select', 'id': 'floatingSelect'}),
            'graveimage': forms.FileInput(attrs={'type': 'file', 'class': 'form-control', 'id': 'exampleInputFile'}),
        }
             
             
# --------------------------- Deceased Information End --------------------------- #

# ---------------------------------------------------------------------------- #
#                                 Grave Images                                 #
# ---------------------------------------------------------------------------- #

class UpdateGraveImage(BSModalModelForm):
    class Meta:
        model = DeceasedInformation
        fields = ['name', 'graveimage']      
        widgets = {
            'name': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': '#', 'readonly': ''}),
            'graveimage': forms.FileInput(attrs={'type': 'file', 'class': 'form-control', 'id': 'exampleInputFile'}),
        }
         
# ------------------------------- Grave Images End ------------------------------- #

# ---------------------------------------------------------------------------- #
#                                   Locations                                  #
# ---------------------------------------------------------------------------- #

class LocationForm(BSModalModelForm):
    class Meta:
        model = Location
        fields = ('__all__')
        widgets = {
            'grave_lot_id': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': '#'}),
            'grave_area': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': '#'}),        
        }
        
# --------------------------------- Locations End -------------------------------- #

# ---------------------------------------------------------------------------- #
#                                Lot Procurement                               #
# ---------------------------------------------------------------------------- #

class CustomerForm(BSModalModelForm):
    
    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.fields['chosen_Lot'].queryset = GardenDetail.objects.filter(Available_Space__gte=1)

    class Meta:
        model = Customer
        fields = ('__all__')
        exclude = ('submitted_by',)
        widgets = {
            'first_Name': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': '#'}),
            'last_Name': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': '#'}),
            'contact_Number': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': '#'}),
            'deceased_Name': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': '#'}),
            'born_Date': forms.TextInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': '#'}),
            'died_Date': forms.TextInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': '#'}),
            'burial_Schedule': forms.TextInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': '#'}),
            'chosen_Lot': forms.Select(attrs={'class': 'form-select'}),
            'chosen_Lot_Type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class GardenDetailForm(BSModalModelForm):
    class Meta:
        model = GardenDetail
        fields = ('__all__')
        widgets = {
            'Lot_Image': forms.FileInput(attrs={'class': 'form-control', 'type': 'file', 'placeholder': '#'}),
            'Garden_Name': forms.Select(attrs={'class': 'form-select', 'placeholder': '#'}),
            'Garden_Description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '#', 'style': 'height: 150px'}),
            'Available_Space': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'placeholder': '#'}),
            'Lot_Type': forms.SelectMultiple(attrs={'class': 'form-select', 'placeholder': '#'})
        }
        
class LotTypeForm(BSModalModelForm):
    class Meta:
        model = LotType
        fields = ('__all__')
        widgets = {
            'Lot_Photo': forms.FileInput(attrs={'class': 'form-control', 'type': 'file', 'placeholder': '#'}),
            'Lot_Name': forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'placeholder': '#'}),
            'Lot_Descriptions': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '#', 'style': 'height: 150px'}),
        }


# ------------------------------ Lot Procurement End ----------------------------- #

# ---------------------------- System Users: Users --------------------------- #

class UserForm(BSModalModelForm, UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields["username"].widget.attrs.update({
            'class': 'form-control enterevent',
            'id': 'username_register',
            'placeholder': '#',
            'required': ''
        })

        self.fields["password1"].widget.attrs.update({
            'class': 'form-control enterevent',
            'id': 'password1',
            'placeholder': '#',
            'required': ''
        })
        
        self.fields["password2"].widget.attrs.update({
            'class': 'form-control enterevent',
            'id': 'password2',
            'placeholder': '#',
            'required': ''
        })
        
        self.fields["first_name"].widget.attrs.update({
            'class': 'form-control enterevent',
            'id': 'name',
            'placeholder': '#',
            'required': ''
        })
    
    class Meta:
        model = User
        fields=['first_name','username','password1','password2', 'is_active']
        
class UpdateUserForm(BSModalModelForm):
    class Meta:
        model = User
        fields=['first_name','username','is_active', 'is_staff', 'is_superuser']
        widgets = {
            'first_name': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': '#'}),
            'username': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'placeholder': '#'}),
        }

# -------------------------- System Users: Users End ------------------------- #