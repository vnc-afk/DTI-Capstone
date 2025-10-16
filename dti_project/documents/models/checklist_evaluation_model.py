from django.db import models
from django.urls import reverse
from django.utils import timezone
from documents.models.base_models import DraftModel
from ..model_choices import REMARKS_CHOICES,STAR_RATING_CHOICES
from users.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class ChecklistEvaluationSheet(DraftModel, models.Model):
    class Meta:
        verbose_name = "Checklist of Requirements and Evaluation Sheet"
        verbose_name_plural = "Checklist of Requirements and Evaluation Sheets"
        
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name_of_business = models.CharField(max_length=255)
    type_of_application = models.CharField(max_length=50, choices=[('New', 'New'), ('Renewal', 'Renewal')])
    renewal_due_date = models.DateField(null=True, blank=True, help_text='Date Expired: Dec 31')
    star_rating = models.PositiveSmallIntegerField(choices=STAR_RATING_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(5)])
    date = models.DateTimeField(default=timezone.now)


    req_application_form = models.BooleanField(
        default=False,
        help_text="Original/e-copy notarized completely filled out application form with Undertaking/Warranty (Minimum of 90 days) signed by the owner or authorized agent..."
    )
    req_application_form_remark = models.CharField(
        max_length=50, choices=REMARKS_CHOICES, blank=True, null=True
    )

    req_business_name_certificate = models.BooleanField(
        default=False,
        help_text="Copy of Valid Business Name Certificate of Registration for Single Proprietorship or Certified true copy of company Partnership..."
    )
    req_business_name_certificate_remark = models.CharField(
        max_length=50, choices=REMARKS_CHOICES, blank=True, null=True
    )

    req_latest_accreditation_certificate = models.BooleanField(
        default=False,
        help_text="Copy of Latest Accreditation Certificate"
    )
    req_latest_accreditation_certificate_remark = models.CharField(
        max_length=50, choices=REMARKS_CHOICES, blank=True, null=True
    )

    req_mechanics_list = models.BooleanField(
        default=False,
        help_text="Original-copy Certified List of Mechanics/Technicians and Position with Personnel/no Data Sheet"
    )
    req_mechanics_list_remark = models.CharField(
        max_length=50, choices=REMARKS_CHOICES, blank=True, null=True
    )

    req_tesda_certificate = models.BooleanField(
        default=False,
        help_text="Copy of valid and relevant TESDA Certificate (National Certificate or Certificate of Competency for Technical Employees)"
    )
    req_tesda_certificate_remark = models.CharField(
        max_length=50, choices=REMARKS_CHOICES, blank=True, null=True
    )

    req_training_list = models.BooleanField(
        default=False,
        help_text="Original/e-copy Certified List of Trainings Attended by the Employees/Technicians within the past 2 years"
    )
    req_training_list_remark = models.CharField(
        max_length=50, choices=REMARKS_CHOICES, blank=True, null=True
    )

    req_tools_equipment_list = models.BooleanField(
        default=False,
        help_text="Original/e-copy List of Shop Tools and Equipment"
    )
    req_tools_equipment_list_remark = models.CharField(
        max_length=50, choices=REMARKS_CHOICES, blank=True, null=True
    )

    req_shop_layout_photos = models.BooleanField(
        default=False,
        help_text="Original/e-copy Shop Floor Plan/Layout/Size/No. of Stalls/Working Bays and interior pictures of the Shop/Office – showing front (with signages) and interior/working area"
    )
    req_shop_layout_photos_remark = models.CharField(
        max_length=50, choices=REMARKS_CHOICES, blank=True, null=True
    )

    req_certification_no_changes = models.BooleanField(
        default=False,
        help_text="Originally issued Certification (in lieu of items 6 and 8) that there are no changes on the said items for renewals, provided that said requirements have been previously submitted"
    )
    req_certification_no_changes_remark = models.CharField(
        max_length=50, choices=REMARKS_CHOICES, blank=True, null=True
    )

    req_comprehensive_insurance = models.BooleanField(
        default=False,
        help_text="Copy of Comprehensive Insurance Policy covering the customer's motor vehicle while in custody and use against theft, pilferage, fire, flood and loss..."
    )
    req_comprehensive_insurance_remark = models.CharField(
        max_length=50, choices=REMARKS_CHOICES, blank=True, null=True
    )

    req_affidavit_on_site_repairs = models.BooleanField(
        default=False,
        help_text="Original Affidavit stating that all services and repairs are done in the clients presence and that they conduct all services and repairs in their client's premises. (In lieu of insurance policy)"
    )
    req_affidavit_on_site_repairs_remark = models.CharField(
        max_length=50, choices=REMARKS_CHOICES, blank=True, null=True
    )

    req_insurance_exemption_proof = models.BooleanField(
        default=False,
        help_text="In places where there are no insurance companies willing to undertake the risk due to the peace and order situation in the area the Director may grant exemption upon sufficient proof of such circumstances"
    )
    req_insurance_exemption_proof_remark = models.CharField(
        max_length=50, choices=REMARKS_CHOICES, blank=True, null=True
    )

    req_dealership_agreement = models.BooleanField(
        default=False,
        help_text="Copy of valid dealership agreement (five star only) Motor Vehicle, Ref and Aircon, Office Machine/Data Processing Equipment)"
    )
    req_dealership_agreement_remark = models.CharField(
        max_length=50, choices=REMARKS_CHOICES, blank=True, null=True
    )

    req_service_contract = models.BooleanField(
        default=False,
        help_text="Copy of Valid Contract of Service, (if any)"
    )
    req_service_contract_remark = models.CharField(
        max_length=50, choices=REMARKS_CHOICES, blank=True, null=True
    )

    req_performance_bond = models.BooleanField(
        default=False,
        help_text="Original copy of Performance Bond policy and official receipt with minimum coverage of P50,000. (in favor of the DTI valid up to December 31, 20__ for 3 to 5 STAR, New or Renewal)"
    )
    req_performance_bond_remark = models.CharField(
        max_length=50, choices=REMARKS_CHOICES, blank=True, null=True
    )

    def __str__(self):
        return self.get_str_display(f"{self.name_of_business} - {self.type_of_application}")
    
    def get_absolute_url(self):
        return reverse("checklist-evaluation-sheet", args=[self.pk])
    
    def get_update_url(self):
        return reverse("update-checklist-evaluation-sheet", args=[self.pk])