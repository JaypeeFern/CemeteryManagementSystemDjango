
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from search.models import DeceasedInformation, Location
from procurement.models import GardenDetail, Customer, LotType
from .forms import *
from .mixins import (
    StaffRequiredMixin,
    SuperuserRequiredMixin,
    SweetifyMixin,
    staff_required,
    superuser_required,
)
from .upload_validation import MAX_UPLOAD_SIZE_BYTES, UPLOAD_SIZE_ERROR_MESSAGE
import sweetify
from django.core.files.storage import FileSystemStorage
import pandas as pd
from tablib import Dataset
from .resources import DeceasedInformationResource
from datetime import datetime   

# Create your views here.

def _is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


# ---------------------------------------------------------------------------- #
#                   Bootstrap Ajax Model Not Class Based View                  #
# ---------------------------------------------------------------------------- #

# def TOAST_SUCCESS(request, message):
#     TOAST_SUCCESS = sweetify.toast(request, message, icon='success', timer=2000)
#     return TOAST_SUCCESS

# def TOAST_ERROR(request, message):
#     TOAST_ERROR = sweetify.toast(request, message, icon='error', timer=2000)
#     return TOAST_ERROR

# def addDeceasedInformation(request):
#     form = DeceasedInfoForm(request=request)
#     if request.method == "POST":
#         form = DeceasedInfoForm(request.POST, request=request)
#         if form.is_valid():
#             if not _is_ajax(request):
#                 form.save()
#                 TOAST_SUCCESS(request,'Data Succesfully Added')
#                 return redirect("Dash_Search")
        
#     return render(request, 'dashboard/modals/add-deceased.html',{
#         'data': DeceasedInformation.objects.all(),
#         'form': form
#     })

# ----------------- Override Class Based View Form Validation ---------------- #
#     def form_valid(self, form):
#         form.instance.is_staff = True
#         form.instance.is_active = True
#         form.save()
#         return super().form_valid(form)
# ------------------------------------- x ------------------------------------ #

# ------------------------------------ End ----------------------------------- #

# ---------------------------------- Alerts ---------------------------------- #

def ADDED_MESSAGE(added):
    ADDED_MESSAGE = f"{added} Succesfully Added"
    return ADDED_MESSAGE

def UPDATED_MESSAGE(updated):
    UPDATED_MESSAGE = f"{updated} Succesfully Updated"
    return UPDATED_MESSAGE

def DELETED_MESSAGE(deleted):
    DELETED_MESSAGE = f"{deleted} Succesfully Deleted"
    return DELETED_MESSAGE

def SWEETIFY_ICON_SUCCESS():
    sweetify_options = {
        'icon': 'success',
        'timer': 1750
    }
    return sweetify_options

# -------------------------------- Alerts End -------------------------------- #

# ---------------------------------------------------------------------------- #
#                                   Dashboard                                  #
# ---------------------------------------------------------------------------- #

@staff_required
def DisplayDashboard(request):
    
    sales_day = Customer.objects.filter(Q(status=True) & Q(date_created__day=datetime.now().day)).values('chosen_Lot__Garden_Name__grave_area').annotate(lot_chosen=Count('chosen_Lot'))
    sales_month = Customer.objects.filter(Q(status=True) & Q(date_created__month=datetime.now().month)).values('chosen_Lot__Garden_Name__grave_area').annotate(lot_chosen=Count('chosen_Lot'))
    sales_year = Customer.objects.filter(Q(status=True) & Q(date_created__year=datetime.now().year)).values('chosen_Lot__Garden_Name__grave_area').annotate(lot_chosen=Count('chosen_Lot'))
 
    model_obj = [
        User.objects.all().last(),
        Customer.objects.all().last(),
        sales_day,
        sales_month,
        sales_year,
        Location.objects.all().last(),
        Location.objects.all(),
        LotType.objects.all().last(),
        DeceasedInformation.objects.all().last(),
    ]
    
    context = {
        'latest_user': model_obj[0],
        'latest_customer': model_obj[1],
        'customers_current_day': model_obj[2],
        'customers_current_month': model_obj[3],
        'customers_current_year': model_obj[4],
        'latest_location': model_obj[5],
        'all_locations': model_obj[6],
        'latest_lottype': model_obj[7],
        'latest_deceased': model_obj[8],
        # # ------------------------------------- x ------------------------------------ #
        'c_accounts': User.objects.filter(Q(is_active=True) & Q(is_staff=False) | Q(is_superuser=False)).count(),
        'c_customers': Customer.objects.filter(status=False).count(),
        'c_staff': User.objects.filter(Q(is_active=True) & Q(is_staff=True) | Q(is_superuser=True)).count(),
        'c_gardens': Location.objects.all().count(),
        'c_lot_types': LotType.objects.all().count(),
        'c_deceased_info': DeceasedInformation.objects.all().count(),
    }
    
    return render(request, "dashboard/index.html", context)

@staff_required
def filterMonth(request):

    # Create If else for form by using the request.method
    if request.method == 'POST':
        get_month = request.POST.get('month_of')
        sales_month = Customer.objects.filter(Q(status=True) & Q(date_created__contains=get_month)).values('chosen_Lot__Garden_Name__grave_area').annotate(lot_chosen=Count('chosen_Lot'))
    else:
        sales_month = Customer.objects.filter(Q(status=True) & Q(date_created__month=datetime.now().month)).values('chosen_Lot__Garden_Name__grave_area').annotate(lot_chosen=Count('chosen_Lot'))

    sales_year = Customer.objects.filter(Q(status=True) & Q(date_created__year=datetime.now().year)).values('chosen_Lot__Garden_Name__grave_area').annotate(lot_chosen=Count('chosen_Lot')) 
    sales_day = Customer.objects.filter(Q(status=True) & Q(date_created__day=datetime.now().day)).values('chosen_Lot__Garden_Name__grave_area').annotate(lot_chosen=Count('chosen_Lot'))
    
    model_obj = [
        User.objects.all().last(),
        Customer.objects.all().last(),
        sales_day,
        sales_month,
        sales_year,
        Location.objects.all().last(),
        Location.objects.all(),
        LotType.objects.all().last(),
        DeceasedInformation.objects.all().last(),
    ]
    
    context = {
        'latest_user': model_obj[0],
        'latest_customer': model_obj[1],
        'customers_current_day': model_obj[2],
        'customers_current_month': model_obj[3],
        'customers_current_year': model_obj[4],
        'latest_location': model_obj[5],
        'all_locations': model_obj[6],
        'latest_lottype': model_obj[7],
        'latest_deceased': model_obj[8],
        # # ------------------------------------- x ------------------------------------ #
        'c_accounts': User.objects.filter(Q(is_active=True) & Q(is_staff=False) | Q(is_superuser=False)).count(),
        'c_customers': Customer.objects.filter(status=False).count(),
        'c_staff': User.objects.filter(Q(is_active=True) & Q(is_staff=True) | Q(is_superuser=True)).count(),
        'c_gardens': Location.objects.all().count(),
        'c_lot_types': LotType.objects.all().count(),
        'c_deceased_info': DeceasedInformation.objects.all().count(),
    }
    
    return render(request, "dashboard/index.html", context)

@staff_required
def filterYear(request):

    # Create If else for form by using the request.method
    if request.method == 'POST':
        get_year = request.POST.get('year_of')
        sales_year = Customer.objects.filter(Q(status=True) & Q(date_created__contains=get_year)).values('chosen_Lot__Garden_Name__grave_area').annotate(lot_chosen=Count('chosen_Lot'))
    else:
        sales_year = Customer.objects.filter(Q(status=True) & Q(date_created__year=datetime.now().year)).values('chosen_Lot__Garden_Name__grave_area').annotate(lot_chosen=Count('chosen_Lot'))
 
    sales_day = Customer.objects.filter(Q(status=True) & Q(date_created__day=datetime.now().day)).values('chosen_Lot__Garden_Name__grave_area').annotate(lot_chosen=Count('chosen_Lot'))
    sales_month = Customer.objects.filter(Q(status=True) & Q(date_created__month=datetime.now().month)).values('chosen_Lot__Garden_Name__grave_area').annotate(lot_chosen=Count('chosen_Lot'))
    model_obj = [
        User.objects.all().last(),
        Customer.objects.all().last(),
        sales_day,
        sales_month,
        sales_year,
        Location.objects.all().last(),
        Location.objects.all(),
        LotType.objects.all().last(),
        DeceasedInformation.objects.all().last(),
    ]
    
    context = {
        'latest_user': model_obj[0],
        'latest_customer': model_obj[1],
        'customers_current_day': model_obj[2],
        'customers_current_month': model_obj[3],
        'customers_current_year': model_obj[4],
        'latest_location': model_obj[5],
        'all_locations': model_obj[6],
        'latest_lottype': model_obj[7],
        'latest_deceased': model_obj[8],
        # # ------------------------------------- x ------------------------------------ #
        'c_accounts': User.objects.filter(Q(is_active=True) & Q(is_staff=False) | Q(is_superuser=False)).count(),
        'c_customers': Customer.objects.filter(status=False).count(),
        'c_staff': User.objects.filter(Q(is_active=True) & Q(is_staff=True) | Q(is_superuser=True)).count(),
        'c_gardens': Location.objects.all().count(),
        'c_lot_types': LotType.objects.all().count(),
        'c_deceased_info': DeceasedInformation.objects.all().count(),
    }
    
    return render(request, "dashboard/index.html", context)

# ------------------------------- Dashboard End ------------------------------ #

# ---------------------------------------------------------------------------- #
#                                 Deceased Data                                #
# ---------------------------------------------------------------------------- #

@staff_required
def renderSearch(request):
    return render(request, 'dashboard/deceased-data.html',{
        'data': DeceasedInformation.objects.all()
    })

class addDeceasedInformation(StaffRequiredMixin, SweetifyMixin, BSModalCreateView):
    model = DeceasedInformation
    template_name = 'dashboard/modals/add-deceased.html'
    form_class = DeceasedInfoForm
    success_message = ADDED_MESSAGE('Data')
    sweetify_options = SWEETIFY_ICON_SUCCESS()
    success_url = reverse_lazy('Dash_Search')
    
class updateDeceasedInformation(StaffRequiredMixin, SweetifyMixin, BSModalUpdateView):
    model = DeceasedInformation
    template_name = 'dashboard/modals/update-deceased.html'
    form_class = DeceasedInfoForm
    success_message = UPDATED_MESSAGE('Data')
    sweetify_options = SWEETIFY_ICON_SUCCESS()
    success_url = reverse_lazy('Dash_Search')

    def get_context_data(self, **kwargs):       
        context = super().get_context_data(**kwargs)
        context['data'] = DeceasedInformation.objects.get(pk=self.kwargs['pk'])
        return context
           
class deleteDeceasedInformation(SuperuserRequiredMixin, SweetifyMixin, BSModalDeleteView):
    model = DeceasedInformation
    template_name = 'dashboard/modals/delete-deceased.html'
    success_message = DELETED_MESSAGE('Data')
    sweetify_options = SWEETIFY_ICON_SUCCESS()
    success_url = reverse_lazy('Dash_Search')
    
    def get_context_data(self, **kwargs):       
        context = super().get_context_data(**kwargs)
        context['data'] = DeceasedInformation.objects.get(pk=self.kwargs['pk'])
        return context
    
@superuser_required
@require_POST
def importCSV(request):
    csv_file = request.FILES.get('csv_file')
    if not csv_file:
        return HttpResponseBadRequest('A CSV file is required.')
    if csv_file.size > MAX_UPLOAD_SIZE_BYTES:
        return HttpResponse(UPLOAD_SIZE_ERROR_MESSAGE, status=413)

    deceased = DeceasedInformationResource()
    dataset = Dataset()
    dataset.load(csv_file.read())
    result = deceased.import_data(dataset, dry_run=True)
    if not result.has_errors():
        deceased.import_data(dataset, dry_run=False)
        return redirect('Dash_Search')
    return redirect('Dash_Search')
 
# ------------------------------------ End ----------------------------------- #

# ---------------------------------------------------------------------------- #
#                                 Grave Images                                 #
# ---------------------------------------------------------------------------- #

@staff_required
def renderGraveImages(request):
    
    return render(request, 'dashboard/grave-images.html', {
        'data': DeceasedInformation.objects.all()
    })
    
class GraveImageUpdate(StaffRequiredMixin, SweetifyMixin, BSModalUpdateView):
    model = DeceasedInformation
    template_name = 'dashboard/modals/update-grave-image.html'
    success_message = UPDATED_MESSAGE('Image')
    sweetify_options = SWEETIFY_ICON_SUCCESS()
    form_class = UpdateGraveImage
    success_url = reverse_lazy('GraveImages')
    
    def get_context_data(self, **kwargs):       
        context = super().get_context_data(**kwargs)
        context['data'] = DeceasedInformation.objects.get(pk=self.kwargs['pk'])
        return context

@superuser_required
@require_POST
def GraveImageDelete(request, pk):
    DeceasedInformation.objects.get(pk=pk).graveimage.delete(save=True)
    sweetify.toast(request, 'Grave Image Deleted', icon='success', timer=2000)
    return redirect('Dash_Search')
    
    
# ----------------------------- Grave Images End ----------------------------- #

# ---------------------------------------------------------------------------- #
#                                   Locations                                  #
# ---------------------------------------------------------------------------- #

@staff_required
def renderLocations(request):
    return render(request, 'dashboard/locations.html', {
        'data': Location.objects.all(),
    })
    
class addLocation(StaffRequiredMixin, SweetifyMixin, BSModalCreateView):
    model = Location
    template_name = 'dashboard/modals/add-location.html'
    form_class = LocationForm
    success_message = ADDED_MESSAGE('Location')
    sweetify_options = SWEETIFY_ICON_SUCCESS()
    success_url = reverse_lazy('Locations')
        
class updateLocation(StaffRequiredMixin, SweetifyMixin, BSModalUpdateView):
    model = Location
    template_name = 'dashboard/modals/update-location.html'
    form_class = LocationForm
    success_message = UPDATED_MESSAGE('Location')
    sweetify_options = SWEETIFY_ICON_SUCCESS()
    success_url = reverse_lazy('Locations')
    
    def get_context_data(self, **kwargs):       
        context = super().get_context_data(**kwargs)
        context['data'] = Location.objects.get(pk=self.kwargs['pk'])
        return context
    
class deleteLocation(SuperuserRequiredMixin, SweetifyMixin, BSModalDeleteView):
    model = Location
    template_name = 'dashboard/modals/delete-location.html'
    success_message = DELETED_MESSAGE('Location')
    sweetify_options = SWEETIFY_ICON_SUCCESS()
    success_url = reverse_lazy('Locations')
    
    def get_context_data(self, **kwargs):       
        context = super().get_context_data(**kwargs)
        context['data'] = Location.objects.get(pk=self.kwargs['pk'])
        return context
    
# ------------------------------- Locations End ------------------------------ #

# ---------------------------------------------------------------------------- #
#                                   Customer                                   #
# ---------------------------------------------------------------------------- #

@staff_required
def renderCustomer(request):
    return render(request, 'dashboard/customer.html',{
        'data': Customer.objects.all(),
    })
    
class addCustomer(StaffRequiredMixin, SweetifyMixin, BSModalCreateView):
    model = Customer
    template_name = 'dashboard/modals/add-customer.html'
    form_class = CustomerForm
    success_message = ADDED_MESSAGE('Customer')
    sweetify_options = SWEETIFY_ICON_SUCCESS()
    success_url = reverse_lazy('Customer')
        
class updateCustomer(StaffRequiredMixin, SweetifyMixin, BSModalUpdateView):
    model = Customer
    template_name = 'dashboard/modals/update-customer.html'
    form_class = CustomerForm
    success_message = UPDATED_MESSAGE('Customer')
    sweetify_options = SWEETIFY_ICON_SUCCESS()
    success_url = reverse_lazy('Customer')
    
    def get_context_data(self, **kwargs):       
        context = super().get_context_data(**kwargs)
        context['data'] = Customer.objects.get(pk=self.kwargs['pk'])
        return context
    
class deleteCustomer(SuperuserRequiredMixin, SweetifyMixin, BSModalDeleteView):
    model = Customer
    template_name = 'dashboard/modals/delete-customer.html'
    success_message = DELETED_MESSAGE('Customer')
    sweetify_options = SWEETIFY_ICON_SUCCESS()
    success_url = reverse_lazy('Customer')
    
    def get_context_data(self, **kwargs):       
        context = super().get_context_data(**kwargs)
        context['data'] = Customer.objects.get(pk=self.kwargs['pk'])
        return context
    
# ------------------------------- End Customer ------------------------------- #

# ---------------------------------------------------------------------------- #
#                                Garden Details                                #
# ---------------------------------------------------------------------------- #

@staff_required
def renderGardenDetails(request):
    return render(request, 'dashboard/garden-details.html',{
        'data': GardenDetail.objects.all()
    })
    
class addGardenDetail(StaffRequiredMixin, SweetifyMixin, BSModalCreateView):
    model = GardenDetail
    template_name = 'dashboard/modals/add-garden-detail.html'
    form_class = GardenDetailForm
    success_message = ADDED_MESSAGE('Garden Details')
    sweetify_options = SWEETIFY_ICON_SUCCESS()
    success_url = reverse_lazy('GardenDetails')

class updateGardenDetail(StaffRequiredMixin, SweetifyMixin, BSModalUpdateView):
    model = GardenDetail
    template_name = 'dashboard/modals/update-garden-detail.html'
    form_class = GardenDetailForm
    success_message = UPDATED_MESSAGE('Garden Details')
    sweetify_options = SWEETIFY_ICON_SUCCESS()
    success_url = reverse_lazy('GardenDetails')
    
    def get_context_data(self, **kwargs):       
        context = super().get_context_data(**kwargs)
        context['data'] = GardenDetail.objects.get(pk=self.kwargs['pk'])
        return context
    
class deleteGardenDetail(SuperuserRequiredMixin, SweetifyMixin, BSModalDeleteView):
    model = GardenDetail
    template_name = 'dashboard/modals/delete-garden-detail.html'
    success_message = DELETED_MESSAGE('Garden Details')
    sweetify_options = SWEETIFY_ICON_SUCCESS()
    success_url = reverse_lazy('GardenDetails')
    
    def get_context_data(self, **kwargs):       
        context = super().get_context_data(**kwargs)
        context['data'] = GardenDetail.objects.get(pk=self.kwargs['pk'])
        return context
    
# ---------------------------- Garden Details End ---------------------------- #

# ---------------------------------------------------------------------------- #
#                                 Garden Images                                #
# ---------------------------------------------------------------------------- #

@staff_required
def renderGardenImage(request):
    return render(request, 'dashboard/garden-images.html',{
        'data': GardenDetail.objects.all()
    })
    
@superuser_required
@require_POST
def deleteGardenImage(request, pk):
    GardenDetail.objects.get(pk=pk).Lot_Image.delete(save=True)
    sweetify.toast(request, 'Garden Image Deleted', icon='success', timer=2000)
    return redirect('GardenImages')
    
# ----------------------------- Garden Image End ----------------------------- #

# ---------------------------------------------------------------------------- #
#                                   Lot Types                                  #
# ---------------------------------------------------------------------------- #

@staff_required
def renderLotTypes(request):
    return render(request, 'dashboard/lot-types.html',{
        'data': LotType.objects.all()
    })
    
class addLotType(StaffRequiredMixin, SweetifyMixin, BSModalCreateView):
    model = LotType
    template_name = 'dashboard/modals/add-lot-type.html'
    form_class = LotTypeForm
    success_message = ADDED_MESSAGE('Lot Type')
    sweetify_options = SWEETIFY_ICON_SUCCESS()
    success_url = reverse_lazy('LotTypes')

class UpdateLotType(StaffRequiredMixin, SweetifyMixin, BSModalUpdateView):
    model = LotType
    template_name = 'dashboard/modals/update-lot-type.html'
    form_class = LotTypeForm
    success_message = UPDATED_MESSAGE('Lot Type')
    sweetify_options = SWEETIFY_ICON_SUCCESS()
    success_url = reverse_lazy('LotTypes')
    
    def get_context_data(self, **kwargs):       
        context = super().get_context_data(**kwargs)
        context['data'] = LotType.objects.get(pk=self.kwargs['pk'])
        return context
    
class DeleteLotType(SuperuserRequiredMixin, SweetifyMixin, BSModalDeleteView):
    model = LotType
    template_name = 'dashboard/modals/delete-lot-type.html'
    success_message = DELETED_MESSAGE('Lot Type')
    sweetify_options = SWEETIFY_ICON_SUCCESS()
    success_url = reverse_lazy('LotTypes')
    
    def get_context_data(self, **kwargs):       
        context = super().get_context_data(**kwargs)
        context['data'] = LotType.objects.get(pk=self.kwargs['pk'])
        return context
    
# ------------------------------- Lot Types End ------------------------------ #

    
# ---------------------------------------------------------------------------- #
#                                     Other                                    #
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
#                                System Accounts                               #
# ---------------------------------------------------------------------------- #

# ----------------------------------- Users ---------------------------------- #

@staff_required
def renderUsers(request):
    context = {
        'data': User.objects.filter(Q(is_superuser=False) & Q(is_staff=False)),
    }
    return render(request, 'dashboard/user-accounts.html',context)

class AddUser(StaffRequiredMixin, SweetifyMixin, BSModalCreateView):
    model = User
    template_name = 'dashboard/modals/add-user.html'
    form_class = UserForm
    success_message = ADDED_MESSAGE('User')
    sweetify_options = SWEETIFY_ICON_SUCCESS()
    success_url = reverse_lazy('SystemUsers')
    
    def form_valid(self, form):
        form.instance.is_active = True
        form.save()
        return super().form_valid(form)
 
@staff_required
def UpdateUser(request, pk):
    user = get_object_or_404(
        User.objects.filter(is_staff=False, is_superuser=False),
        pk=pk,
    )
    form = UpdateUserForm(instance=user, request=request)
    if request.method == "POST":
        form = UpdateUserForm(request.POST, instance=user, request=request)
        if form.is_valid():
            if not _is_ajax(request):
                new_password = form.cleaned_data['new_password']
                if new_password != '':
                    user.set_password(new_password)
                    user.save()
                form.save()
                sweetify.toast(request, 'Account Succesfully Updated', icon="success", timer=2000)
                return redirect("SystemUsers")
    return render(request, 'dashboard/modals/update-user.html',{'form':form,'data': user})
    
class DeleteUser(SuperuserRequiredMixin, SweetifyMixin, BSModalDeleteView):
    model = User
    template_name = 'dashboard/modals/delete-user.html'
    success_message = DELETED_MESSAGE('User')
    sweetify_options = SWEETIFY_ICON_SUCCESS()
    success_url = reverse_lazy('SystemUsers')

    def get_queryset(self):
        return super().get_queryset().filter(is_staff=False, is_superuser=False)
    
    def get_context_data(self, **kwargs):       
        context = super().get_context_data(**kwargs)
        context['data'] = User.objects.get(pk=self.kwargs['pk'])
        return context
    
# --------------------------------- End Users -------------------------------- #

# ----------------------------------- Staff ---------------------------------- #

@superuser_required
def renderStaff(request):
    context = {
        'data': User.objects.filter(Q(is_active=True) and Q(is_superuser=True) | Q(is_staff=True)),
    }
    return render(request, 'dashboard/staff-accounts.html',context)

@superuser_required
def AddStaff(request):
    form = UserForm(request=request)
    if request.method == "POST":
        form = UserForm(request.POST, request=request)
        if form.is_valid():
            if not _is_ajax(request):
                staff = request.POST.get('is_staff')
                admin = request.POST.get('is_superuser')
                
                form.instance.is_active = True
                if staff == 'on':
                    form.instance.is_staff = True
                elif admin == 'on':
                    form.instance.is_staff = True
                    form.instance.is_superuser = True
              
                form.save()
                if staff == 'on':
                    sweetify.toast(request, 'Staff Account Succesfully Created', icon="success", timer=2000)
                elif admin == 'on':
                    sweetify.toast(request, 'Admin Account Succesfully Updated', icon="success", timer=2000)
                return redirect("SystemStaff")
    return render(request, 'dashboard/modals/add-staff.html',{'form':form})

@superuser_required
def UpdateStaff(request, pk):
    user = User.objects.get(pk=pk)
    form = UpdateStaffForm(instance=user, request=request)
    if request.method == "POST":
        form = UpdateStaffForm(request.POST, instance=user, request=request)
        if form.is_valid():
            if not _is_ajax(request):
                new_password = form.cleaned_data['new_password']

                if new_password != '':
                    user.set_password(new_password)
                    user.save()
                
                form.save()
                sweetify.toast(request, 'Staff Account Succesfully Updated', icon="success", timer=2000)
                return redirect("SystemStaff")
    return render(request, 'dashboard/modals/update-staff.html',{'form':form,'data': user})

class DeleteStaff(SuperuserRequiredMixin, SweetifyMixin, BSModalDeleteView):
    model = User
    template_name = 'dashboard/modals/delete-staff.html'
    success_message = DELETED_MESSAGE('User')
    sweetify_options = SWEETIFY_ICON_SUCCESS()
    success_url = reverse_lazy('SystemUsers')
    
    def get_context_data(self, **kwargs):       
        context = super().get_context_data(**kwargs)
        context['data'] = User.objects.get(pk=self.kwargs['pk'])
        return context
    
# --------------------------------- End Staff -------------------------------- #
