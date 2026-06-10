from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from ..mixins.permissions_mixins import PreventAdminFormPostRequestMixin, RoleFormPageRestrictionMixin
from ..mixins.context_mixins import PreviewContextMixin
from ..mixins.form_mixins import FormStepsMixin, FormSubmissionMixin, FormsetMixin, MessagesMixin
from ..mixins.service_mixins import ServiceCategoryMixin
from ..utils.form_helpers import get_certification_text
from ..constants import (
    CHECKLIST_EVALUATION_DETAIL_GROUPS,
    CHECKLIST_EVALUATION_FIELD_GROUPS,
    INSPECTION_VALIDATION_DETAIL_GROUPS,
    INSPECTION_VALIDATION_REPORT_FIELD_GROUPS,
    ORDER_OF_PAYMENT_DETAIL_GROUPS,
    ORDER_OF_PAYMENT_FIELD_GROUPS,
    OTHER_BUSINESS_NAME_RELATED_DETAIL_GROUPS,
    OTHER_BUSINESS_NAME_RELATED_FIELD_GROUPS,
    PERSONAL_DATA_SHEET_DETAIL_GROUPS,
    PERSONAL_DATA_SHEET_FIELD_GROUPS,
    SALES_PROMOTION_DETAIL_GROUPS,
    SALES_PROMOTION_FIELD_GROUPS,
    SERVICE_REPAIR_ACCREDITATION_DETAIL_GROUPS,
    SERVICE_REPAIR_ACCREDITATION_FIELD_GROUPS
)
from ..forms import (
    FORMSET_CLASSES,
    ChecklistEvaluationSheetForm,
    InspectionValidationReportForm,
    OrderOfPaymentForm,
    PersonalDataSheetForm,
    SalesPromotionPermitApplicationForm,
    ServiceRepairAccreditationApplicationForm,
    OtherBusinessNameRelatedForm,
)
from ..models import (
    ChecklistEvaluationSheet,
    InspectionValidationReport,
    OrderOfPayment,
    PersonalDataSheet,
    SalesPromotionPermitApplication,
    ServiceRepairAccreditationApplication,
    OtherBusinessNameRelatedFormModel
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.template.loader import render_to_string


class BaseCreateView(
    LoginRequiredMixin,
    PreviewContextMixin,
    MessagesMixin,
    FormSubmissionMixin,
    FormStepsMixin,
    FormsetMixin,
    RoleFormPageRestrictionMixin,
    CreateView
):
    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        if request.headers.get("x-requested-with") == "XMLHttpRequest" and action == "preview":
            return self.handle_ajax_preview(request)
        return super().post(request, *args, **kwargs)

    def handle_ajax_preview(self, request):
        self.object = None
        form = self.get_form(self.get_form_class())
        if form.is_valid():
            if not hasattr(self, 'formset_classes') or not self.formset_classes:
                context = self.get_preview_context(form)
                return JsonResponse(context)
            temp_obj = form.save(commit=False)
            temp_obj.user = request.user
            formsets = self.get_formsets(instance=temp_obj)
            if self.formsets_valid(formsets):
                context = self.get_preview_context(form)
                return JsonResponse(context)
            else:
                self.form_invalid(form, action="preview")
        else:
            self.form_invalid(form, action="preview")

        messages_html = render_to_string("documents/partials/alerts_container.html", {
            "messages": messages.get_messages(request)
        })
        response_data = {
            "errors": form.errors,
            "messages_html": messages_html
        }
        return JsonResponse(response_data, status=400)

    # Pass user to forms for autofill
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class CreateSalesPromotionView(BaseCreateView):
    template_name = 'documents/create_templates/create_sales_promotion.html'
    model = SalesPromotionPermitApplication
    context_object_name = 'sales_promo'
    form_class = SalesPromotionPermitApplicationForm
    formset_classes = {'product': FORMSET_CLASSES['product_covered']}
    FIELD_GROUPS = SALES_PROMOTION_FIELD_GROUPS
    detail_groups = SALES_PROMOTION_DETAIL_GROUPS
    additional_sections = ['coverage']
    allowed_roles = ['business_owner', 'authorized_official']

    def get_success_url(self):
        return reverse_lazy('sales-promotion-application', kwargs={'pk': self.object.pk})

class CreateOtherBusinessRelatedFormView(BaseCreateView):
    template_name = 'documents/create_templates/create_other_business_related_form.html'
    model = OtherBusinessNameRelatedFormModel
    context_object_name = 'form'
    form_class = OtherBusinessNameRelatedForm
    FIELD_GROUPS = OTHER_BUSINESS_NAME_RELATED_FIELD_GROUPS
    detail_groups = []
    allowed_roles = ['business_owner', 'authorized_official']
    detail_groups = OTHER_BUSINESS_NAME_RELATED_DETAIL_GROUPS
    allowed_roles = ['business_owner''authorized_official']

    def get_success_url(self):
        return reverse_lazy('other-business-related', kwargs={'pk': self.object.pk})

class CreatePersonalDataSheetView(BaseCreateView):
    template_name = 'documents/create_templates/create_personal_data_sheet.html'
    model = PersonalDataSheet
    form_class = PersonalDataSheetForm
    allowed_roles = ['business_owner', 'authorized_official']

    formset_classes = {
        'employee_background': FORMSET_CLASSES['employee_background'],
        'trainings_attended': FORMSET_CLASSES['trainings_attended'],
        'educational_attainment': FORMSET_CLASSES['educational_attainment'],
        'character_references': FORMSET_CLASSES['character_references'],
    }
    context_object_name = 'personal_data'
    FIELD_GROUPS = PERSONAL_DATA_SHEET_FIELD_GROUPS
    detail_groups = PERSONAL_DATA_SHEET_DETAIL_GROUPS

    def form_valid(self, form):
        personal_data_sheet = form.save(commit=False)
        personal_data_sheet.user = self.request.user
        personal_data_sheet.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('personal-data-sheet', kwargs={'pk': self.object.pk})


class CreateServiceRepairAccreditationApplicationView(BaseCreateView):
    template_name = 'documents/create_templates/create_service_repair.html'
    model = ServiceRepairAccreditationApplication
    form_class = ServiceRepairAccreditationApplicationForm
    FIELD_GROUPS = SERVICE_REPAIR_ACCREDITATION_FIELD_GROUPS
    detail_groups = SERVICE_REPAIR_ACCREDITATION_DETAIL_GROUPS
    allowed_roles = ['business_owner', 'authorized_official']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = ServiceRepairAccreditationApplication(
            name_of_business=self.request.user,
            warranty_period=30
        )
        context['warranty_text'] = application.get_warranty_text()
        return context

    def get_success_url(self):
        return reverse_lazy('service-repair-accreditation', kwargs={'pk': self.object.pk})


class CreateInspectionValidationReportView(BaseCreateView, ServiceCategoryMixin):
    model = InspectionValidationReport
    template_name = 'documents/create_templates/create_inspection_validation_report.html'
    form_class = InspectionValidationReportForm
    FIELD_GROUPS = INSPECTION_VALIDATION_REPORT_FIELD_GROUPS
    detail_groups = INSPECTION_VALIDATION_DETAIL_GROUPS
    additional_sections = ['service_categories']
    allowed_roles = ['collection_agent', 'alt_collection_agent']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['certification_text'] = get_certification_text()
        context['service_categories'] = self.get_service_categories_with_services()
        return context

    def get_success_url(self):
        return reverse_lazy('inspection-validation-report', kwargs={'pk': self.object.pk})


class CreateOrderOfPaymentView(BaseCreateView):
    model = OrderOfPayment
    template_name = 'documents/create_templates/create_order_of_payment.html'
    form_class = OrderOfPaymentForm
    FIELD_GROUPS = ORDER_OF_PAYMENT_FIELD_GROUPS
    detail_groups = ORDER_OF_PAYMENT_DETAIL_GROUPS
    allowed_roles = ['collection_agent', 'alt_collection_agent', 'admin']
  
    def get_initial(self):
        initial = super().get_initial()
        sppa_id = self.request.GET.get('sppa')
        if sppa_id:
            try:
                sppa = SalesPromotionPermitApplication.objects.get(pk=sppa_id, status='approved')
                if hasattr(sppa, 'order_of_payment'):
                    messages.error(self.request, "An Order of Payment already exists for this SPPA.")
                    return {}
                initial['sales_promotion_permit_application'] = sppa
            except SalesPromotionPermitApplication.DoesNotExist:
                messages.error(self.request, "Invalid or unapproved SPPA.")
        return initial
    
    def form_valid(self, form):
        # Accept SPPA id from:
        #  - explicit field in POST: 'sales_promotion_permit_application'
        #  - short POST param added by JS: 'sppa'
        #  - fallback GET param: 'sppa'
        sppa_val = (
            self.request.POST.get('sales_promotion_permit_application')
            or self.request.POST.get('sppa')
            or self.request.GET.get('sppa')
        )

        if not sppa_val:
            form.add_error(None, "Sales Promotion Application is missing.")
            return self.form_invalid(form)

        # Normalize to integer pk if possible
        sppa_pk = None
        try:
            sppa_pk = int(sppa_val)
        except (TypeError, ValueError):
            # attempt to extract digits from a model repr if needed
            import re
            m = re.search(r'\d+', str(sppa_val))
            if m:
                try:
                    sppa_pk = int(m.group())
                except (TypeError, ValueError):
                    sppa_pk = None

        if not sppa_pk:
            form.add_error(None, "Invalid Sales Promotion Application identifier.")
            return self.form_invalid(form)

        try:
            sppa = SalesPromotionPermitApplication.objects.get(pk=sppa_pk, status='approved')
        except SalesPromotionPermitApplication.DoesNotExist:
            form.add_error(None, "Invalid or unapproved SPPA.")
            return self.form_invalid(form)

        # Prevent duplicate OOPs for the same SPPA (explicit query avoids relying on related_name)
        if OrderOfPayment.objects.filter(sales_promotion_permit_application=sppa).exists():
            form.add_error(None, "An Order of Payment already exists for this SPPA.")
            return self.form_invalid(form)

        # Link SPPA and user before saving
        form.instance.sales_promotion_permit_application = sppa
        form.instance.user = self.request.user

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('order-of-payment', kwargs={'pk': self.object.pk})


class CreateChecklistEvaluationSheetView(BaseCreateView):
    model = ChecklistEvaluationSheet
    template_name = 'documents/create_templates/create_checklist_evaluation_sheet.html'
    form_class = ChecklistEvaluationSheetForm
    FIELD_GROUPS = CHECKLIST_EVALUATION_FIELD_GROUPS
    detail_groups = CHECKLIST_EVALUATION_DETAIL_GROUPS
    allowed_roles = ['collection_agent', 'alt_collection_agent']
    
    def get_success_url(self):
        return reverse_lazy('checklist-evaluation-sheet', kwargs={'pk': self.object.pk})
