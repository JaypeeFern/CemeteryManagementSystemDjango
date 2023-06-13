
from django import forms
from .models import Customer, GardenDetail

class CustomerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.fields['chosen_Lot'].queryset = GardenDetail.objects.filter(Available_Space__gte=1)
        
    class Meta:
        model = Customer
        fields = ('submitted_by', 'first_Name', 'last_Name', 'contact_Number', 'deceased_Name', 'born_Date', 'died_Date', 'burial_Schedule', 'chosen_Lot', 'chosen_Lot_Type')
        widgets = {
            'first_Name': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'id': 'floatingName', 'placeholder': '#'}),
            'last_Name': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'id': 'floatinglastName', 'placeholder': '#'}),
            'contact_Number': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'id': 'floatingContact', 'placeholder': '#'}),
            'deceased_Name': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'id': 'floatingDeceasedName', 'placeholder': '#'}),
            'born_Date': forms.TextInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'floatingDeceasedBirth', 'placeholder': '#'}),
            'died_Date': forms.TextInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'floatingDeceasedDied', 'placeholder': '#'}),
            'burial_Schedule': forms.TextInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'floatingDeceasedBuriel', 'placeholder': '#'}),
            'chosen_Lot': forms.Select(attrs={'class': 'form-select', 'id': "floatingChosenLot"}),
            'chosen_Lot_Type': forms.Select(attrs={'class': 'form-select', 'id': "floatingChosenLotType"}),
        }
