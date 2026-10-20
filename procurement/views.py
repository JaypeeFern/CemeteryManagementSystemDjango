import mimetypes

from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from .models import GardenDetail, LotType, Customer
from .forms import CustomerForm
from search.models import Location
from django.db.models import F
from django.db import transaction
from django.views.decorators.http import require_POST
import sweetify


PUBLIC_IMAGE_CONTENT_TYPES = {
    'image/bmp',
    'image/gif',
    'image/jpeg',
    'image/png',
    'image/tiff',
    'image/webp',
}


@require_GET
def public_media_asset(request, name):
    if not name.startswith(('GardenImages/', 'Images/', 'lot_photo/')):
        raise Http404

    content_type, _ = mimetypes.guess_type(name)
    if content_type not in PUBLIC_IMAGE_CONTENT_TYPES:
        raise Http404

    is_public_garden_image = GardenDetail.objects.filter(Lot_Image=name).exists()
    is_public_lot_photo = LotType.objects.filter(Lot_Photo=name).exists()
    if not is_public_garden_image and not is_public_lot_photo:
        raise Http404

    storage = FileSystemStorage(location=settings.MEDIA_ROOT)
    try:
        image_file = storage.open(name, 'rb')
    except (FileNotFoundError, SuspiciousFileOperation, ValueError):
        raise Http404

    response = FileResponse(image_file, content_type=content_type)
    response['Cache-Control'] = 'public, max-age=3600'
    response['X-Content-Type-Options'] = 'nosniff'
    return response

# Create your views here.

def RenderLotProcurement(request):
    
    # Variables 
    form = CustomerForm()
    gardenDetails = GardenDetail.objects.all()
    lotType = LotType.objects.all()
    location = Location.objects.all()
    customer = (
        Customer.objects.filter(submitted_by=request.user)
        if request.user.is_authenticated
        else Customer.objects.none()
    )
    
    main_context = {
        'data': gardenDetails,
        'data2': lotType,
        'data3': location,
        'data4': customer,
        'form': form
    }
    
    return render(request, 'procurement/index.html', main_context)

@login_required(login_url='Home')
@require_POST
def customerForm(request):
    form = CustomerForm(request.POST)
    if form.is_valid():
        with transaction.atomic():
            chosen_lot_id = form.cleaned_data['chosen_Lot'].pk
            space_reserved = GardenDetail.objects.filter(
                pk=chosen_lot_id,
                Available_Space__gte=1,
            ).update(Available_Space=F('Available_Space') - 1)

            if space_reserved:
                customer = form.save(commit=False)
                customer.submitted_by = request.user
                customer.save()
                form.save_m2m()
                sweetify.success(
                    request,
                    'Succesfully Submitted!',
                    text='Please wait for SMPI Personnel to contact you for the next process. Have a nice day!',
                    persistent='Close',
                )
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
