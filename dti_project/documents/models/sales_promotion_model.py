from django.db import models
from django.urls import reverse
from ..models.base_models import BaseApplication, DraftModel
from django.utils import timezone
from users.models import User

class SalesPromotionPermitApplication(DraftModel, BaseApplication):
    class Meta:
        verbose_name = "Sales Promotion Permit Application"
        verbose_name_plural = "Sales Promotion Permit Applications"

    promo_title = models.CharField(max_length=255)

    sponsor_name = models.CharField(max_length=255)
    sponsor_address = models.TextField()
    sponsor_telephone = models.CharField(max_length=50, blank=True)
    sponsor_email = models.EmailField(blank=True)
    sponsor_authorized_rep = models.CharField(max_length=255)
    sponsor_designation = models.CharField(max_length=255)

    advertising_agency_name = models.CharField(max_length=255, blank=True)
    advertising_agency_address = models.TextField(blank=True)
    advertising_agency_telephone = models.CharField(max_length=50, blank=True)
    advertising_agency_email = models.EmailField(blank=True)
    advertising_agency_authorized_rep = models.CharField(max_length=255, blank=True)
    advertising_agency_designation = models.CharField(max_length=255, blank=True)

    promo_period_start = models.DateField(null=True, blank=True)
    promo_period_end = models.DateField(null=True, blank=True)

    COVERAGE_CHOICES = [
        ('NCR', 'NCR or several regions including Metro Manila'),
        ('2_REGIONS', '2 regions or more outside NCR'),
        ('1_REGION_2_PROVINCES', 'Single region covering 2 provinces or more'),
        ('1_PROVINCE', 'Single province')
    ]

    coverage = models.CharField(max_length=20, choices=COVERAGE_CHOICES)

    region_location_of_sponsor = models.CharField(max_length=255, blank=True)
    regions_covered = models.TextField(blank=True)
    single_region = models.CharField(max_length=255, blank=True)
    provinces_covered = models.TextField(blank=True)
    single_province = models.CharField(max_length=255, blank=True)
    cities_or_municipalities_covered = models.TextField(blank=True)

    def __str__(self):
        return self.get_str_display(self.promo_title)

    def get_absolute_url(self):
        return reverse("sales-promotion-application", args=[self.pk])

    def get_update_url(self):
        return reverse("update-sales-promotion", args=[self.pk])
    
class ProductCovered(models.Model):
    permit_application = models.ForeignKey(SalesPromotionPermitApplication, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    specifications = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.brand}"