from django.urls import path
from . import views

urlpatterns = [
    path('regions/', views.get_regions, name='regions'),
    path('provinces/<int:region_id>/', views.get_provinces, name='provinces'),
    path('cities/<int:province_id>/', views.get_cities, name='cities'),
    path('barangays/<int:city_id>/', views.get_barangays, name='barangays'),
]
