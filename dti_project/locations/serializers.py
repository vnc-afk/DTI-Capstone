from rest_framework import serializers
from .models import Region, Province, CityMunicipality, Barangay

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name', 'code']

class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['id', 'name', 'code', 'region']

class CityMunicipalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CityMunicipality
        fields = ['id', 'name', 'code', 'province']

class BarangaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Barangay
        fields = ['id', 'name', 'code', 'city']
