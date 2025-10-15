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
    ServiceRepairAccreditationApplicationForm
)
from ..models import (
    ChecklistEvaluationSheet,
    InspectionValidationReport,
    OrderOfPayment,
    PersonalDataSheet,
    SalesPromotionPermitApplication,
    ServiceRepairAccreditationApplication
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
    PreventAdminFormPostRequestMixin,
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
                self.form_invalid(form, action="preview", formsets=formsets)
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
    allowed_roles = ['business_owner']

    def get_success_url(self):
        return reverse_lazy('sales-promotion-application', kwargs={'pk': self.object.pk})


class CreatePersonalDataSheetView(BaseCreateView):
    template_name = 'documents/create_templates/create_personal_data_sheet.html'
    model = PersonalDataSheet
    form_class = PersonalDataSheetForm
    allowed_roles = ['business_owner']

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
    allowed_roles = ['business_owner']

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
    allowed_roles = ['collection_agent']

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
    allowed_roles = ['collection_agent']

    def get_success_url(self):
        return reverse_lazy('order-of-payment', kwargs={'pk': self.object.pk})


class CreateChecklistEvaluationSheetView(BaseCreateView):
    model = ChecklistEvaluationSheet
    template_name = 'documents/create_templates/create_checklist_evaluation_sheet.html'
    form_class = ChecklistEvaluationSheetForm
    FIELD_GROUPS = CHECKLIST_EVALUATION_FIELD_GROUPS
    detail_groups = CHECKLIST_EVALUATION_DETAIL_GROUPS
    allowed_roles = ['collection_agent']
    
    def get_success_url(self):
        return reverse_lazy('checklist-evaluation-sheet', kwargs={'pk': self.object.pk})
