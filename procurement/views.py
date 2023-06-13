from django.shortcuts import render, redirect
from .models import GardenDetail, LotType, Customer
from .forms import CustomerForm
from search.models import Location
from django.db.models import F
import sweetify

# Create your views here.

def RenderLotProcurement(request):
    
    # Variables 
    form = CustomerForm()
    gardenDetails = GardenDetail.objects.all()
    lotType = LotType.objects.all()
    location = Location.objects.all()
    customer = Customer.objects.filter(submitted_by=request.user)
    
    main_context = {
        'data': gardenDetails,
        'data2': lotType,
        'data3': location,
        'data4': customer,
        'form': form
    }
    
    return render(request, 'procurement/index.html', main_context)

def customerForm(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            chosenLot = request.POST['chosen_Lot']
            data = GardenDetail.objects.filter(pk=chosenLot)
            convertQuery = data.values('Available_Space')
            
            for availableSpace in convertQuery:
                print(availableSpace)
                if availableSpace['Available_Space'] >= 1:
                    convertQuery.update(Available_Space=F('Available_Space') - 1)
                    form.save()
                    sweetify.success(request, 'Succesfully Submitted!', text='Please wait for SMPI Personnel to contact you for the next process. Have a nice day!', persistent='Close') 
                    for data in data:
                        data.save()
                    return redirect('Procurement')
        return redirect('Procurement')











# ---------------------------------------------------------------------------- #
#                           Garden Capacity Function                           #
# ---------------------------------------------------------------------------- #

# def RenderLotProcurement(request):
    
#     # Variables 
#     form = CustomerForm()
#     gardenDetails = GardenDetail.objects.all()
#     lotType = LotType.objects.all()
#     location = Location.objects.all()
#     customer = Customer.objects.filter(submitted_by=request.user)
    
#     main_context = {
#         'data': gardenDetails,
#         'data2': lotType,
#         'data3': location,
#         'data4': customer,
#         'form': form
#     }
    
#     if request.method == 'POST':
#         form = CustomerForm(request.POST)
#         if form.is_valid():
#             chosenLot = request.POST['chosen_Lot']
#             data = GardenDetail.objects.filter(pk=chosenLot)
#             convertQuery = data.values('Available_Space')
            
#             for availableSpace in convertQuery:
#                 if availableSpace['Available_Space'] >= 1:
#                     convertQuery.update(Available_Space=F('Available_Space') - 1)
#                     form.save()
#                     sweetify.success(request, 'Succesfully Submitted!', text='Please wait for SMPI Personnel to contact you for the next process. Have a nice day!', persistent='Close') 
#                     for data in data:
#                         data.save()
#                 elif availableSpace['Available_Space'] <= 0:
#                     sweetify.error(request, 'Error!', text='The lot you have chosen does not have any space left. Please choose another lot. Thank you ', persistent='Close')
#                     error_context = {
#                         'data': gardenDetails,
#                         'data2': lotType,
#                         'data3': location,
#                         'form': form
#                     }
#                     return render(request, 'procurement/index.html', error_context)
#                 else:
#                     form = CustomerForm()    
#                     return render(request, 'procurement/index.html', main_context)
#     return render(request, 'procurement/index.html', main_context)

# ---------------------------------------------------------------------------- #
#                                       x                                      #
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
#                             Lot Capacity Function                            #
# ---------------------------------------------------------------------------- #

# def customerForm(request):
#     if request.method == 'POST':
#         form = CustomerForm(request.POST)
#         if form.is_valid():
#             chosen_Lot_Type = request.POST['chosen_Lot_Type'] 
#             data = LotType.objects.filter(pk=chosen_Lot_Type)
#             convertQuery = data.values('Lot_Capacity')
            
#             for lotSpace in convertQuery:
#                 if lotSpace['Lot_Capacity'] >= 1:
#                     convertQuery.update(Lot_Capacity=F('Lot_Capacity') - 1)
#                     form.save()
#                     sweetify.success(request, 'Succesfully Submitted!', text='Please wait for SMPI Personnel to contact you for the next process. Have a nice day!', persistent='Close')
#                     for data in data:
#                         data.save() 
#                     return redirect('Procurement')   
#     return redirect('Procurement')

# ---------------------------------------------------------------------------- #
#                                       x                                      #
# ---------------------------------------------------------------------------- #