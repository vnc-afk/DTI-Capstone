from django.http import JsonResponse
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Value, F, DateTimeField
from django.db.models.functions import Coalesce
from django.db.models import Q
from django.db.models.functions import Concat

from documents.models import (
    ChecklistEvaluationSheet,
    InspectionValidationReport,
    OrderOfPayment,
    PersonalDataSheet,
    SalesPromotionPermitApplication,
    ServiceRepairAccreditationApplication,
)
from documents.constants import MODEL_URLS
from documents.mixins.permissions_mixins import UserRoleMixin
from users.models import User


# -------------------------------
# DASHBOARD VIEW
# -------------------------------
class DashboardView(LoginRequiredMixin, UserRoleMixin, TemplateView):
    template_name = "dashboard/dashboard.html"

    @staticmethod
    def get_queryset_or_all(model, user):
        """Return queryset depending on user role (admin sees more)."""
        if user.role == "admin":
            qs = model.objects.filter(
                Q(status="draft", user=user) | ~Q(status="draft")
            )
        else:
            qs = model.objects.filter(user=user)

        # Determine which datetime fields exist
        available_fields = [f.name for f in model._meta.get_fields()]
        datetime_fields = []
        if 'date_filed' in available_fields:
            datetime_fields.append('date_filed')
        if 'date' in available_fields:
            datetime_fields.append('date')

        if len(datetime_fields) >= 2:
            # Use Coalesce if 2+ fields
            qs = qs.annotate(
                sort_date=Coalesce(*datetime_fields, output_field=DateTimeField())
            ).order_by('-sort_date', '-id')
        elif len(datetime_fields) == 1:
            # Only one datetime field exists, order by it directly
            qs = qs.order_by(f'-{datetime_fields[0]}', '-id')
        else:
            # No datetime field exists, fallback to ordering by id
            qs = qs.order_by('-id')

        return qs.only('pk', 'id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Pre-fetched querysets
        sales_promos = self.get_queryset_or_all(SalesPromotionPermitApplication, user)
        personal_data_sheets = self.get_queryset_or_all(PersonalDataSheet, user)
        service_accreditations = self.get_queryset_or_all(
            ServiceRepairAccreditationApplication, user
        )
        inspection_reports = self.get_queryset_or_all(InspectionValidationReport, user)
        orders_of_payment = self.get_queryset_or_all(OrderOfPayment, user)
        checklist_evaluation_sheets = self.get_queryset_or_all(
            ChecklistEvaluationSheet, user
        )

        # Sections for dashboard tiles
        sections = [
            {
                "title": "Sales Promotion Applications",
                "data": sales_promos,
                "url": "sales-promotion-application",
            },
            {
                "title": "Personal Data Sheets",
                "data": personal_data_sheets,
                "url": "personal-data-sheet",
            },
            {
                "title": "Service & Repair Accreditations",
                "data": service_accreditations,
                "url": "service-repair-accreditation",
            },
            {
                "title": "Inspection Reports",
                "data": inspection_reports,
                "url": "inspection-validation-report",
            },
            {
                "title": "Orders of Payment",
                "data": orders_of_payment,
                "url": "order-of-payment",
            },
            {
                "title": "Checklist Evaluation Sheets",
                "data": checklist_evaluation_sheets,
                "url": "checklist-evaluation-sheet",
            },
        ]

        context.update(
            {
                "sales_promos": sales_promos,
                "personal_data_sheets": personal_data_sheets,
                "service_accreditations": service_accreditations,
                "inspection_reports": inspection_reports,
                "orders_of_payment": orders_of_payment,
                "checklist_evaluation_sheets": checklist_evaluation_sheets,
                "sections": sections,  # ✅ use this in template loop
            }
        )
        return context


# -------------------------------
# SEARCH SUGGESTIONS VIEW
# -------------------------------
class SearchSuggestionsView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        query = request.GET.get("query", "").strip()

        response_data = {
            "role": user.role,
            "users": [],
            "user_count": 0,
            "documents": {"results": [], "count": 0},
        }

        if not query:
            return JsonResponse(response_data)

        # Models included in search
        document_models = [
            SalesPromotionPermitApplication,
            PersonalDataSheet,
            ServiceRepairAccreditationApplication,
            OrderOfPayment,
            InspectionValidationReport,
            ChecklistEvaluationSheet,
        ]

        search_fields = [
            "promo_title",
            "name_of_business",
            "name",
            "first_name",
            "middle_name",
            "last_name",
        ]

        # --- ADMIN: search users + all documents ---
        if user.role == "collection_agent":
            users_qs = (
                User.objects.annotate(
                    full_name=Concat(F("first_name"), Value(" "), F("last_name"))
                )
                .filter(full_name__icontains=query)
                .exclude(role="collection_agent")
            )

            response_data["users"] = [
                {
                    "id": u.id,
                    "full_name": u.full_name,
                    "profile_picture": u.profile_picture.url
                    if u.profile_picture
                    else "",
                    "role": u.role.replace("_", " ").title(),
                    "link": '/users/profile',
                }
                for u in users_qs
            ]
            response_data["user_count"] = users_qs.count()

            # Search all documents (no user restriction)
            for model in document_models:
                self._search_documents(
                    model, query, response_data, restrict_to_user=False
                )

        # --- BUSINESS OWNER: only their own documents ---
        elif user.role == "business_owner":
            for model in document_models:
                self._search_documents(
                    model, query, response_data, restrict_to_user=True, user=user
                )

        elif user.role == 'admin':
            # Admin can search users (like collection_agent)
            users_qs = (
                User.objects.annotate(
                    full_name=Concat(F("first_name"), Value(" "), F("last_name"))
                )
                .filter(full_name__icontains=query)
            )

            response_data["users"] = [
                {
                    "id": u.id,
                    "full_name": u.full_name,
                    "profile_picture": u.profile_picture.url
                    if u.profile_picture
                    else "",
                    "role": u.role.replace("_", " ").title(),
                    "link": '/users/profile',
                }
                for u in users_qs
            ]
            response_data["user_count"] = users_qs.count()

            # Admin can search all documents (no user restriction)
            for model in document_models:
                self._search_documents(
                    model, query, response_data, restrict_to_user=False
                )
            

        return JsonResponse(response_data)

    # -------------------------------
    # HELPER METHOD
    # -------------------------------
    @staticmethod
    def _search_documents(model, query, response_data, restrict_to_user=False, user=None):
        """Reusable document search logic for admin and business owner."""
        search_fields = [
            "promo_title",
            "name_of_business",
            "name",
            "first_name",
            "middle_name",
            "last_name",
        ]

        model_fields = [f.name for f in model._meta.fields]
        matched_field = None
        qs = model.objects.exclude(status="draft") if not restrict_to_user else model.objects.all()

        if "first_name" in model_fields and "last_name" in model_fields:
            qs = qs.annotate(
                full_name=Concat(
                    F("first_name"),
                    Value(" "),
                    F("middle_name"),
                    Value(" "),
                    F("last_name"),
                )
            )
            matched_field = "full_name"
        else:
            for field in search_fields:
                if field in model_fields:
                    matched_field = field
                    break

        if not matched_field:
            return

        filter_kwargs = {f"{matched_field}__icontains": query}
        if restrict_to_user and "user" in model_fields:
            filter_kwargs["user"] = user

        qs = qs.filter(**filter_kwargs)

        serialized_docs = [
            {
                "id": obj.id,
                "model": model._meta.verbose_name,
                "link": MODEL_URLS[model.__name__],
                "display": getattr(obj, matched_field, str(obj)),
            }
            for obj in qs
        ]

        response_data["documents"]["results"].extend(serialized_docs)
        response_data["documents"]["count"] += qs.count()
