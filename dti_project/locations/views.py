from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Region, Province, CityMunicipality, Barangay
from .serializers import RegionSerializer, ProvinceSerializer, CityMunicipalitySerializer, BarangaySerializer


@api_view(['GET'])
def get_regions(request):
    """Return all regions."""
    regions = Region.objects.all().order_by('name').values('id', 'name', 'code')  # Use values() for speed
    return Response(list(regions))


@api_view(['GET'])
def get_provinces(request, region_id):
    """Return all provinces within a region."""
    provinces = Province.objects.filter(region_id=region_id).order_by('name').values('id', 'name', 'code')
    return Response(list(provinces))


@api_view(['GET'])
def get_cities(request, province_id):
    """Return all cities or municipalities within a province."""
    cities = CityMunicipality.objects.filter(province_id=province_id).order_by('name').values('id', 'name', 'code')
    return Response(list(cities))


@api_view(['GET'])
def get_barangays(request, city_id):
    """Return all barangays within a city or municipality."""
    # This is likely the slowest - barangays can be hundreds per city
    barangays = Barangay.objects.filter(city_id=city_id).order_by('name').values('id', 'name', 'code')
    return Response(list(barangays))