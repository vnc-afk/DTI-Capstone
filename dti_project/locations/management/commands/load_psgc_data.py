import requests
from django.core.management.base import BaseCommand
from locations.models import Region, Province, CityMunicipality, Barangay

PSGC_BASE_URL = "https://psgc.gitlab.io/api"

# class Command(BaseCommand):
#     help = "Fetches and loads all PSGC data (regions, provinces, cities, barangays) into the database."

#     def handle(self, *args, **options):
#         self.stdout.write(self.style.SUCCESS("🚀 Fetching PSGC data..."))

#         # --- 1. Fetch Regions ---
#         regions = requests.get(f"{PSGC_BASE_URL}/regions/").json()
#         for r in regions:
#             Region.objects.update_or_create(
#                 code=r.get("code"),
#                 defaults={"name": r.get("name")}
#             )
#         self.stdout.write(self.style.SUCCESS(f"✅ Loaded {len(regions)} regions."))

#         # --- 2. Fetch Provinces ---
#         provinces = requests.get(f"{PSGC_BASE_URL}/provinces/").json()
#         for p in provinces:
#             region_code = p.get("regionCode")
#             try:
#                 region = Region.objects.get(code=region_code)
#                 Province.objects.update_or_create(
#                     code=p.get("code"),
#                     defaults={
#                         "name": p.get("name"),
#                         "region": region
#                     }
#                 )
#             except Region.DoesNotExist:
#                 self.stdout.write(self.style.WARNING(f"⚠️ Skipping province {p.get('name')} - region not found"))
#         self.stdout.write(self.style.SUCCESS(f"✅ Loaded {len(provinces)} provinces."))

#         # --- 3. Fetch Cities/Municipalities ---
#         cities = requests.get(f"{PSGC_BASE_URL}/cities-municipalities/").json()
#         for c in cities:
#             province_code = c.get("provinceCode")
#             try:
#                 province = Province.objects.get(code=province_code)
#                 CityMunicipality.objects.update_or_create(
#                     code=c.get("code"),
#                     defaults={
#                         "name": c.get("name"),
#                         "province": province
#                     }
#                 )
#             except Province.DoesNotExist:
#                 self.stdout.write(self.style.WARNING(f"⚠️ Skipping city {c.get('name')} - province not found"))
#         self.stdout.write(self.style.SUCCESS(f"✅ Loaded {len(cities)} cities/municipalities."))

#         # --- 4. Fetch Barangays ---
#         barangays = requests.get(f"{PSGC_BASE_URL}/barangays/").json()
#         for b in barangays:
#             city_code = b.get("cityCode") or b.get("municipalityCode")
#             try:
#                 city = CityMunicipality.objects.get(code=city_code)
#                 Barangay.objects.update_or_create(
#                     code=b.get("code"),
#                     defaults={
#                         "name": b.get("name"),
#                         "city": city
#                     }
#                 )
#             except CityMunicipality.DoesNotExist:
#                 self.stdout.write(self.style.WARNING(f"⚠️ Skipping barangay {b.get('name')} - city/municipality not found"))
#         self.stdout.write(self.style.SUCCESS(f"✅ Loaded {len(barangays)} barangays."))

#         self.stdout.write(self.style.SUCCESS("🎉 PSGC data successfully loaded!"))
