from django.contrib import admin
from .models import Region, Province, CityMunicipality, Barangay

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    search_fields = ['name', 'code']

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    search_fields = ['name', 'code']
    list_filter = ['region']           # filter provinces by region
    autocomplete_fields = ['region']   # dynamic lookup for region

@admin.register(CityMunicipality)
class CityMunicipalityAdmin(admin.ModelAdmin):
    search_fields = ['name', 'code']
    list_filter = ['province']            # filter cities by parent province
    autocomplete_fields = ['province']    # dynamic lookup

@admin.register(Barangay)
class BarangayAdmin(admin.ModelAdmin):
    search_fields = ['name', 'code']
    list_filter = ['city']               # filter barangays by parent city
    autocomplete_fields = ['city']       # dynamic lookup
