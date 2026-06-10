from datetime import timedelta
from django.db import models
from django.urls import reverse
from django.utils import timezone

class CollectionReport(models.Model):
    report_items = models.ManyToManyField(
        'CollectionReportItem',
        related_name='collection_reports',
        blank=True  # Allow empty reports for daily auto-creation
    )
    dti_office = models.CharField(max_length=255, blank=True, null=True)
    report_collection_date = models.DateField(null=True, blank=True, unique=True)  # Add unique constraint
    report_no = models.CharField(max_length=255, blank=True, null=True, unique=True)  # Should be unique
    date_from = models.DateField(null=True, blank=True)
    responsibility_center_code = models.CharField(max_length=50, blank=True, null=True)
    date_to = models.DateField(null=True, blank=True)
    rc_code = models.CharField(max_length=50, null=True, blank=True)

    # Summary
    undeposited_last_report = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        help_text="Undeposited Collections Last Report"
    )
    undeposited_this_report = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        help_text="Undeposited Collections This Report"
    )

    collections_this_report = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        help_text="Collections per OR Numbers: "
    )

    
    total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    certification = models.TextField(blank=True, null=True)
    name_of_collection_officer = models.CharField(max_length=255, blank=True, null=True)
    official_designation = models.CharField(max_length=255, blank=True, null=True) 

    class Meta:
        # Ensure only one report per day - use unique on field instead
        ordering = ['-report_collection_date']
        indexes = [
            models.Index(fields=['-report_collection_date']),
        ]

    def date_range_display(self):
        """Return a readable date range, preferring stored dates over calculated ones."""
        # Use stored date range if available
        if self.date_from and self.date_to:
            if self.date_from == self.date_to:
                return self.date_from.strftime("%b %d, %Y")
            else:
                return f"{self.date_from.strftime('%b %d, %Y')} - {self.date_to.strftime('%b %d, %Y')}"
        
        # Fall back to calculating from report items
        dates = list(self.report_items.values_list('date', flat=True).filter(date__isnull=False))
        if not dates:
            # If no items with dates, use report_collection_date
            if self.report_collection_date:
                return self.report_collection_date.strftime("%b %d, %Y")
            return "No dates"

        first_date = min(dates)
        last_date = max(dates)

        if first_date == last_date:
            return first_date.strftime("%b %d, %Y")
        else:
            return f"{first_date.strftime('%b %d, %Y')} - {last_date.strftime('%b %d, %Y')}"
        
    def report_duration(self):
        """Determine if the report is daily, monthly, or yearly based on report item dates."""
        dates = list(self.report_items.values_list('date', flat=True).filter(date__isnull=False))
        
        if not dates:
            return "Daily"  # Default for empty reports (like auto-created daily reports)
        
        # Get the earliest and latest dates
        first_date = min(dates)
        last_date = max(dates)

        # Calculate the date difference
        date_diff = last_date - first_date

        # Determine report type
        if date_diff <= timedelta(days=1):
            return "Daily"
        elif date_diff <= timedelta(days=30 * 2):  # Approx 2 months
            return "Monthly"
        else:
            return "Yearly"

    def __str__(self):
        """Display report based on duration type"""
        duration = self.report_duration()
        
        if duration == "Yearly":
            # For yearly reports, just show the year
            if self.date_to:
                return f"Report {self.date_to.year}"
            elif self.report_collection_date:
                return f"Report {self.report_collection_date.year}"
            else:
                # Fall back to getting year from report items
                dates = list(self.report_items.values_list('date', flat=True).filter(date__isnull=False))
                if dates:
                    return f"Report {min(dates).year}"
                return "Yearly Report"
        else:
            # For daily and monthly, show full date range
            return f"Report ({self.report_no}) - {self.date_range_display()}"

    def delete(self, *args, **kwargs):
        # Delete all associated report items first
        self.report_items.all().delete()
        # Then delete the report itself
        super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("collection-report", args=[self.pk])


class CollectionReportItem(models.Model):
    # General information
    date = models.DateField(default=timezone.now)
    number = models.CharField(max_length=50, blank=True, null=True, help_text='Official Receipt Number')
    rc_code = models.CharField(max_length=50, blank=True, null=True)
    payor = models.CharField(max_length=255, blank=True, null=True)
    particulars = models.CharField(max_length=255, blank=True, null=True)

    
    # Core amounts
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    stamp_tax = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    # I. Other Service Income (628)

    ## 1. Main Header (Other service income)
    # 1a. BN Registration
    bn_original = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="BN Original")
    bn_renewal = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="BN Renewal")

    # 1b. Accreditation
    accreditation_original = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    accreditation_renewal = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    accreditation_filing_fee = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    truck_rebuilding_original = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    truck_rebuilding_renewal = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    # 1c. Sales Promo
    sales_promo_fee = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    sales_promo_revisions = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    # 1d. Licensing and Certifications
    certification = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    bulk_sales = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    assessment_fee = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    license_fee = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    # 1e. PETC and Miscellaneous
    petc_accreditation = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    bn_listings = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    confiscated_materials = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    # 2. Fines and Penalties
    # 2a. Admin 
    fines_penalties = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="Fines and Penalties (629)")

    # 2b. Surcharge
    surcharge_bn_reg = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="Surcharge BN Registration")
    surchage_accreditation = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="Surcharge Accreditation")

    # Miscellaneous income (678)
    misc_income = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.payor} - {self.number or 'No OR'}"
    
    def get_absolute_url(self):
        return reverse("collection-report-item", args=[self.pk]) 
