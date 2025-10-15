from django.db import models
from django.urls import reverse
from ..model_choices import APPLICATION_OR_ACTIVITY_CHOICES, OFFICE_SHOP_CHOICES, RECOMMENDATION_CHOICES, SERVICE_CATEGORY_CHOICES
from ..models.base_models import DraftModel, YesNoField
from django.utils import timezone
from users.models import User

class InspectionValidationReport(DraftModel, models.Model):
    class Meta:
        verbose_name = "Inspection Validation Report"
        verbose_name_plural = "Inspection Validation Reports"

    # Basic Information
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name_of_business = models.CharField(max_length=255)
    address = models.TextField()
    date = models.DateField(default=timezone.now)
    type_of_application_activity = models.CharField(max_length=50, choices=APPLICATION_OR_ACTIVITY_CHOICES)

    # Basic Info Section
    years_in_service = models.PositiveIntegerField(null=True, blank=True)
    types_of_office_shop = models.CharField(max_length=30, choices=OFFICE_SHOP_CHOICES, default='Main', help_text='Type of Office/Shop')

    business_name_cert = YesNoField(help_text='Business Name Certificates')
    business_name_cert_remarks = models.TextField(blank=True)

    accreditation_cert = YesNoField(help_text='Accreditation Certificate')
    accreditation_cert_remarks = models.TextField(blank=True)

    service_rates = YesNoField()
    service_rates_remarks = models.TextField(blank=True)

    # C. Tools and Equipment
    tools_equipment_complete = YesNoField()
    tools_equipment_serial_no = models.CharField(max_length=255, blank=True)
    racmac_sres_recovery_machine = YesNoField(help_text="For RAC/MAC SREs, with recovery machine")
    racmac_serial_no = models.CharField(max_length=255, blank=True)
    proof_acquisition_recovery_machine = models.CharField(max_length=255, blank=True, help_text="Proof of acquisition of recovery machine")

    # D. Competence of Technicians
    employed_technicians_count = models.PositiveIntegerField(null=True, blank=True)
    average_technician_experience = models.PositiveIntegerField(null=True, blank=True, help_text="Experience in years")
    tesda_certification_nc = models.CharField(max_length=255, blank=True)
    tesda_certification_coc = models.CharField(max_length=255, blank=True)
    continuous_training_program = YesNoField(help_text="For RAC/MAC, with continuous training program for mechanics/technicians?")
    list_employees_past_2_years = YesNoField(help_text="Has submitted trainings of employees for the past 2 years?")
    refrigerant_storage_disposal_system = models.CharField(max_length=255, null=True, blank=True, help_text="For RAC/MAC, with refrigerant recovery storage and disposal system consistent with existing enivronmental laws and regulations")

    # E. Facilities
    office_work_area_sqm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Size of shop/work area? (sq.m)")
    working_stalls_count = models.PositiveIntegerField(null=True, blank=True, help_text="No. of working stalls/bays")
    tool_equipment_storage_existing = YesNoField(help_text="Tool and equipment storage existing?")
    tool_equipment_storage_adequate = YesNoField(help_text="Adequate")
    existing_record_keeping_system = YesNoField(help_text="Existing Record keeping system")
    customers_reception_waiting_area_existing = YesNoField(help_text="Customers reception and waiting area exists?")
    customers_reception_waiting_area_adequate = YesNoField("Adequate?")
    customers_reception_waiting_area_suitable = YesNoField(help_text="Suitable?")
    fire_extinguishers_count = models.PositiveIntegerField(null=True, blank=True, help_text="No. of applicable and unexpired fire extinguishers?")
    available_personal_protective_equipment = models.CharField(max_length=255, blank=True, help_text="Available person protective equipment")
    available_medical_kit= YesNoField(max_length=255, blank=True, help_text="Medical Kit")
    security_personnel_count = models.PositiveIntegerField(null=True, blank=True, help_text="No. of security Personnel")
    inflammable_areas = models.CharField(max_length=255, blank=True, help_text="Areas for inflammables such as gasoline, oil, paint, etc.")

    # F. Type of Insurance Coverage
    type_of_insurance_coverage = models.CharField(max_length=255, blank=True, help_text="Type of Insurance Coverage?")
    insurance_expiry_date = models.DateField(null=True, blank=True)
    insurance_coverage_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Amount in PHP")

    # G. Customer Satisfaction Feedback (CSF) and Complaint Handling
    complaints_handling_process_exists = YesNoField(help_text="With complaints handling process?")
    complaints_handling_process_documented = YesNoField(help_text="Documented?")
    customer_satisfaction_feedback_form_exists = YesNoField(help_text="With customer satisfaction feedback? (CSF)")

    # H. Findings/Remarks
    findings_remarks = models.TextField(blank=True, help_text='Findings/Remarks')

    # I. Recommendation
    recommendation = models.CharField(max_length=50, choices=RECOMMENDATION_CHOICES, blank=True, null=True)
    inspected_by_accreditation_officer = models.CharField(max_length=255, blank=True, help_text='Inspected by: (Accreditation Officer/Leader)')
    inspected_by_member = models.CharField(max_length=255, blank=True, help_text='Inspected by: (Member)')

    authorized_signatory_name = models.CharField(max_length=255, blank=True)
    authorized_signatory_date = models.DateField(null=True, blank=True)

    # Add M2M if using services
    services_offered = models.ManyToManyField('Service', blank=True, related_name="inspection_reports")

    class Meta:
        verbose_name = "Inspection and Validation Report"
        verbose_name_plural = "Inspection and Validation Reports"
        ordering = ['-date']

    def __str__(self):
        return self.get_str_display(f"{self.name_of_business} - {self.date} - {self.type_of_application_activity}")
    
    def get_absolute_url(self):
        return reverse("inspection-validation-report", args=[self.pk])
    
    def get_update_url(self):
        return reverse("update-inspection-validation-report", args=[self.pk])
        
    def get_recommendation_display(self):
        """Return a human-readable list of selected recommendations"""
        recommendations = []
        if self.recommendation_approval:
            recommendations.append("Approval")
        if self.recommendation_disapproval:
            recommendations.append("Disapproval")
        if self.recommendation_monitoring_issuance_sco:
            recommendations.append("Monitoring/Issuance of SCO")
        if self.recommendation_new_application:
            recommendations.append("New Application")
        if self.recommendation_renewal_application:
            recommendations.append("Renewal Application")
        if self.recommendation_continuing_accreditation:
            recommendations.append("Continuing Accreditation")
        return ", ".join(recommendations) if recommendations else "No recommendations selected"
    
    def group_services_by_category(self):
        grouped = {}
        for service in self.services_offered.prefetch_related('category').all():
            category_name = service.category.name
            grouped.setdefault(category_name, []).append(service)

        return grouped