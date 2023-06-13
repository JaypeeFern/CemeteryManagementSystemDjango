from django.urls import path
from home import views
from . import views

urlpatterns = [
    path('', views.DisplayDashboard, name="Dashboard"),
    path('month', views.filterMonth, name='FilterMonth'),
    path('year', views.filterYear, name='FilterYear'),
    path('deceased-data/', views.renderSearch, name='Dash_Search'),
    path('deceased-data/add', views.addDeceasedInformation.as_view(), name='Dash_Add'),
    path('deceased-data/update/<int:pk>', views.updateDeceasedInformation.as_view(), name='Update'),
    path('deceased-data/delete/<str:pk>', views.deleteDeceasedInformation.as_view(), name='Delete'),
    path('deceased-data/importcsv', views.importCSV, name='ImportCSV'),
    # ------------------------------------- x ------------------------------------ #
    path('grave-images', views.renderGraveImages, name='GraveImages'),
    path('grave-images/update/<int:pk>', views.GraveImageUpdate.as_view(), name='UpdateImage'),
    path('grave-images/delete/<str:pk>', views.GraveImageDelete, name='DeleteImage'),
    # ------------------------------------- x ------------------------------------ #
    path('locations', views.renderLocations, name='Locations'),
    path('locations/add', views.addLocation.as_view(), name='AddLocation'),
    path('locations/update/<int:pk>', views.updateLocation.as_view(), name='UpdateLocation'),
    path('locations/delete/<int:pk>', views.deleteLocation.as_view(), name='DeleteLocation'),
    # ------------------------------------- x ------------------------------------ #
    path('customer', views.renderCustomer, name='Customer'),
    path('customer/add', views.addCustomer.as_view(), name='AddCustomer'),
    path('customer/update/<int:pk>', views.updateCustomer.as_view(), name='UpdateCustomer'),
    path('customer/delete/<int:pk>', views.deleteCustomer.as_view(), name='DeleteCustomer'),
    # ------------------------------------- x ------------------------------------ #
    path('garden-details', views.renderGardenDetails, name='GardenDetails'),
    path('garden-details/add', views.addGardenDetail.as_view(), name='AddGarden'),
    path('garden-details/update/<int:pk>', views.updateGardenDetail.as_view(), name='UpdateGarden'),
    path('garden-details/delete/<int:pk>', views.deleteGardenDetail.as_view(), name='DeleteGarden'),
    # ------------------------------------- x ------------------------------------ #
    path('garden-images', views.renderGardenImage, name='GardenImages'),
    path('garden-images/delete/<int:pk>', views.deleteGardenImage, name='DeleteGardenImage'),
    # ------------------------------------- x ------------------------------------ #
    path('lot-types', views.renderLotTypes, name='LotTypes'),
    path('lot-types/add', views.addLotType.as_view(), name='AddLotType'),
    path('lot-types/update/<int:pk>', views.UpdateLotType.as_view(), name='UpdateLotType'),
    path('lot-types/delete/<int:pk>', views.DeleteLotType.as_view(), name='DeleteLotType'),
    # ------------------------------------- x ------------------------------------ #
    path('system-users', views.renderUsers, name='SystemUsers'),
    path('system-users/add', views.AddUser.as_view(), name='AddUser'),
    path('system-users/update/<int:pk>', views.UpdateUser, name='UpdateUser'),
    path('system-users/delete/<int:pk>', views.DeleteUser.as_view(), name='DeleteUser'),
    # ------------------------------------- x ------------------------------------ #
    path('system-staff', views.renderStaff, name='SystemStaff'),
    path('system-staff/add', views.AddStaff, name='AddStaff'),
    path('system-staff/update/<int:pk>', views.UpdateStaff, name='UpdateStaff'),
    path('system-staff/delete/<int:pk>', views.DeleteStaff.as_view(), name='DeleteStaff'),
]   