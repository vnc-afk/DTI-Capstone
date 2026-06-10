from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView, TemplateView, View
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout as auth_logout, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.contrib import messages
import logging

from users.mixins import FormSubmissionMixin
from users.models import User
from .forms import CustomLoginForm, CustomUserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import AddStaffForm
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
import random, string
from .forms import AddStaffForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils import timezone 
from .forms import AddStaffForm

from django.db.models import Q
from documents.models import (
    # Base models
    BaseApplication,
    DraftModel,
    YesNoField,
    PeriodModel,
    
    # Checklist evaluation
    ChecklistEvaluationSheet,
    
    # Inspection validation
    InspectionValidationReport,
    
    # Order of payment
    OrderOfPayment,
    
    # Personal data sheet models
    PersonalDataSheet,
    EmployeeBackground,
    TrainingsAttended,
    EducationalAttainment,
    CharacterReference,
    
    # Sales promotion models
    SalesPromotionPermitApplication,
    ProductCovered,
    
    # Service repair accreditation models
    ServiceRepairAccreditationApplication,
    Service,
    ServiceCategory,
)

logger = logging.getLogger(__name__)

# Create your views here.


#forgot password view
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth import login
from django.urls import reverse
from .forms import ForgotPasswordForm, ResetPasswordForm
from .models import User  # adjust if your User model is custom
import random

# -----------------------------
# FORGOT PASSWORD
# -----------------------------
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

#Settings View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from .models import ActivityLog
from .utils import log_activity



class ForgotPasswordView(View):
    template_name = 'users/forgot_password.html'

    def get(self, request):
        form = ForgotPasswordForm()
        return render(request, self.template_name, {
            'form': form,
            'verification_type': 'reset_password',
            'verification_sent': False
        })

    def post(self, request):
        form = ForgotPasswordForm(request.POST)
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

        if not form.is_valid():
            if is_ajax:
                return JsonResponse({
                    "success": False,
                    "error": "Invalid email format."
                })
            return render(request, self.template_name, {
                'form': form,
                'verification_type': 'reset_password',
                'verification_sent': False
            })

        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            if is_ajax:
                return JsonResponse({
                    "success": False,
                    "error": "Email not found."
                })
            messages.error(request, "Email not found.")
            return render(request, self.template_name, {
                'form': form,
                'verification_type': 'reset_password',
                'verification_sent': False
            })

        # ✅ Generate OTP and store
        user.generate_secure_otp_code()
        user.save()

        # ✅ Save info to session
        request.session['pending_verification_user'] = user.id
        request.session['reset_email'] = user.email

        # ✅ Debug log
        print(f"[DEBUG] Password reset code for {email}: {user.verification_code}")

        # ✅ Masked email (e.g., "te***@gmail.com")
        def mask_email(email):
            username, domain = email.split('@')
            masked_username = username[0] + "***" + username[-1] if len(username) > 2 else username[0] + "***"
            return f"{masked_username}@{domain}"

        if is_ajax:
            return JsonResponse({
                "success": True,
                "masked_email": mask_email(email)
            })

        # For normal form POST (fallback)
        return render(request, self.template_name, {
            'form': form,
            'verification_type': 'reset_password',
            'verification_sent': True,
            'email': email
        })


# -----------------------------
# RESET PASSWORD
# -----------------------------
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.urls import reverse

User = get_user_model()

class ResetPasswordView(View):
    template_name = 'users/reset_password.html'

    def get(self, request):
        email = request.session.get('reset_email')
        if not email:
            messages.error(request, "Your session has expired. Please restart the password reset process.")
            return redirect('forgot_password')
        return render(request, self.template_name)

    def post(self, request):
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.session.get('reset_email')

        if not email:
            return JsonResponse({
                'success': False,
                'message': 'Session expired. Please restart the password reset process.'
            })

        if not password or not confirm_password:
            return JsonResponse({
                'success': False,
                'message': 'Please fill out both password fields.'
            })

        if password != confirm_password:
            return JsonResponse({
                'success': False,
                'message': 'Passwords do not match.'
            })

        if len(password) < 8:
            return JsonResponse({
                'success': False,
                'message': 'Password must be at least 8 characters long.'
            })

        try:
            user = User.objects.get(email=email)
            user.password = make_password(password)
            user.save()

            # ✅ Clean up session and add success message
            request.session.pop('reset_email', None)
            request.session.pop('pending_verification_user', None)

            messages.success(request, "Your password has been successfully reset! You can now sign in.")

            return JsonResponse({
                'success': True,
                'redirect': reverse('sign-in')
            })

        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'No user account found for this email.'
            })

# staff account view
from django.contrib.auth import get_user_model
from django.shortcuts import render

User = get_user_model()

def staff_accounts_view(request):
    staff_users = User.objects.filter(role__in=['collection_agent', 'alt_collection_agent', 'authorized_official'])
    return render(request, 'users/staff_accounts.html', {'staff_users': staff_users})

#add staff view
User = get_user_model()


def add_staff(request):
    if request.method == 'POST':
        form = AddStaffForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data.get('default_address', '')
            phone = form.cleaned_data.get('default_phone', '')
            birthday = form.cleaned_data.get('birthday')
            role = request.POST.get('role', 'collection_agent')

            today = timezone.localdate()
            if birthday >= today:
                form.add_error('birthday', 'Birthday must be in the past.')
                return render(request, 'users/add_staff.html', {'form': form})

            # Generate email based on role
            if role == 'collection_agent':
                base_email = f"{last_name.lower()}.dti.agent@gmail.com"
            elif role == 'alt_collection_agent':
                base_email = f"{last_name.lower()}.dti.alt@gmail.com"
            else:  # authorized_official or default staff
                base_email = f"{last_name.lower()}.dti.staff@gmail.com"

            email = base_email
            counter = 1
            while User.objects.filter(email=email).exists():
                email = f"{last_name.lower()}{counter}@{base_email.split('@')[1]}"
                counter += 1

            username = email.split('@')[0]

            # 🔐 Generate password in the format LastnameYYYYMMDD
            formatted_birthday = birthday.strftime("%Y%m%d")
            password = f"{last_name.capitalize()}{formatted_birthday}"

            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                role=role,
                is_staff=True,
            )

            user.default_address = address
            user.default_phone = phone
            user.birthday = birthday
            user.save()

            return render(request, 'users/add_staff.html', {
                'form': AddStaffForm(),
                'show_popup': True,
                'popup_email': email,
                'popup_password': password,
                'user_id': user.id,
            })
    else:
        form = AddStaffForm()

    return render(request, 'users/add_staff.html', {'form': form})

# Staff Created Popup View
from django.shortcuts import render

def staff_created_popup(request):
    email = request.session.get('new_staff_email')
    password = request.session.get('new_staff_password')

    context = {
        'email': email,
        'password': password,
    }

    return render(request, 'users/staff_created_popup.html', context)

# Delete New Staff View

User = get_user_model()

def delete_new_staff(request, user_id):
    """Delete the newly created staff account."""
    try:
        User.objects.filter(id=user_id).delete()
        messages.success(request, "Newly created account deleted.")
    except Exception as e:
        messages.error(request, f"Error deleting account: {e}")
    return redirect('staff_accounts')

#Settings View
from documents.verification import VerificationDocument  # correct import
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.core.paginator import Paginator

class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = "users/settings.html"
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user

        # ✅ Pending verification status
        context['has_pending_verification'] = VerificationDocument.objects.filter(
            user=user, status='pending'
        ).exists()

        # ✅ Activity logs visible to the user
        logs = ActivityLog.get_visible_logs(user)

        paginator = Paginator(logs, self.paginate_by)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context['activity_logs'] = page_obj.object_list
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()
        context['total_activities'] = logs.count()

        # ✅ Admin flag
        context['is_admin'] = user.role == User.Roles.ADMIN

        return context


#Profile Detail View
class ProfileDetailView(DetailView):
        model = User
        template_name = "users/profile.html"
        context_object_name = "profile"
    
        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            profile = self.get_object()
    
            # Document queries
            sales_promos = SalesPromotionPermitApplication.objects.filter(user=profile)
            personal_data_sheets = PersonalDataSheet.objects.filter(user=profile)
            # only include VERIFIED service repair accreditations for the transaction history
            service_accreditations = ServiceRepairAccreditationApplication.objects.filter(
                user=profile,
                payment_status=ServiceRepairAccreditationApplication.PaymentStatus.VERIFIED
            )
            inspection_reports = InspectionValidationReport.objects.filter(user=profile)
            # only include VERIFIED orders of payment for the transaction history
            orders_of_payment = OrderOfPayment.objects.filter(
                payment_status=OrderOfPayment.PaymentStatus.VERIFIED
            ).filter(
                Q(user=profile) | Q(sales_promotion_permit_application__user=profile)
            ).select_related('sales_promotion_permit_application')
            checklist_evaluation_sheets = ChecklistEvaluationSheet.objects.filter(user=profile)
    
            # Total count
            total_documents = (
                sales_promos.count()
                + personal_data_sheets.count()
                + service_accreditations.count()
                + inspection_reports.count()
                + orders_of_payment.count()
                + checklist_evaluation_sheets.count()
            )
    
            # Build transaction history (combined list of dicts)
            from decimal import Decimal
            import datetime
    
            def _pick_date(obj):
                # prefer acknowledgment/verification timestamps, then other common date fields
                return (
                    getattr(obj, "acknowledgment_generated_at", None)
                    or getattr(obj, "date_paid", None)
                    or getattr(obj, "date", None)
                    or getattr(obj, "date_filed", None)
                    or getattr(obj, "created_at", None)
                    or None
                )
    
            transactions = []
    
            # OOP transactions (sales promos)
            for oop in orders_of_payment:
                display_ref = oop.reference_code or f"OOP-{oop.pk}"
                # prefer the Sales Promotion name when available
                app_name = None
                if getattr(oop, "sales_promotion_permit_application", None):
                    sppa = oop.sales_promotion_permit_application
                    app_name = getattr(sppa, "sponsor_name", None) or str(sppa)

                transactions.append({
                    "date": _pick_date(oop),
                    "reference": display_ref,
                    "label": app_name or "Sales Promotion",
                    "amount": oop.total_amount or Decimal("0.00"),
                    "status": str(getattr(oop, "payment_status", "")).title(),
                })

            # Service Repair Accreditation transactions (verified only)
            for sra in service_accreditations:
                transactions.append({
                    "date": _pick_date(sra),
                    "reference": sra.reference_code or f"SRA-{sra.pk}",
                    "label": getattr(sra, "name_of_business", str(sra)),
                    "amount": sra.total_amount or (sra.calculate_fee() if hasattr(sra, "calculate_fee") else Decimal("0.00")),
                    "status": str(getattr(sra, "payment_status", "")).title(),
                })
    
            # sort newest first; None dates go to the end
            def _sort_key(t):
                return t["date"] or datetime.datetime.min.replace(tzinfo=None)
    
            transactions.sort(key=_sort_key, reverse=True)
    
            # Add to context
            context.update({
                "sales_promos": sales_promos,
                "personal_data_sheets": personal_data_sheets,
                "service_accreditations": service_accreditations,
                "inspection_reports": inspection_reports,
                "orders_of_payment": orders_of_payment,
                "checklist_evaluation_sheets": checklist_evaluation_sheets,
                "total_documents": total_documents,
                "transactions": transactions,
            })
            return context

class StaffListView(ListView):
    model = User
    template_name = 'users/staff_accounts.html'
    context_object_name = 'staff_users'  # easier name in template

    def get_queryset(self):
        # Include all staff roles
        return User.objects.filter(
            role__in=['collection_agent', 'alt_collection_agent', 'authorized_official']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = 'staff'
        return context
    
#List all business owners (verified + unverified)
from django.views.generic import ListView
from users.models import User

class BusinessOwnerListView(ListView):
    model = User
    template_name = 'users/bo_accounts.html'
    context_object_name = 'businesshumans'

    def get_queryset(self):
        # Return both verified and unverified business owners
        return User.objects.filter(
            role__in=['unverified_owner', 'business_owner']
        ).order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['businesshumans'] = self.get_queryset()  # keep naming consistent
        context['user_type'] = 'business_owner'
        return context


#admin side verify
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from users.models import User
from notifications.models import Notification

def verify_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "verify":
            user.role = User.Roles.BUSINESS_OWNER
            user.save()

            # Notification for the user
            Notification.objects.create(
                user=user,
                sender=request.user,
                message="Your account has been verified successfully.",
                type="approved",
                url=None
            )

            # Success message for admin
            messages.success(request, f"{user.get_full_name()} has been verified successfully.")

        elif action == "deny":
            user.role = User.Roles.UNVERIFIED_OWNER
            user.save()

            # Delete all verification documents
            user.verification_documents.all().delete()

            # Notification for the user
            Notification.objects.create(
                user=user,
                sender=request.user,
                message="Your verification documents were rejected as invalid.",
                type="rejected",
                url=None
            )

            # Warning message for admin
            messages.warning(request, f"{user.get_full_name()}'s verification documents were denied.")

        return redirect("bo_accounts")

    # For GET request, show verification documents (if admin wants to view)
    documents = user.verification_documents.all()
    return render(request, "users/view_verification.html", {"user": user, "documents": documents})

# One-click verify user
class VerifyUserView(View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.role = User.Roles.BUSINESS_OWNER
        user.is_verified = True
        user.save()
        # Optional: mark any VerificationRequest as verified
        VerificationRequest.objects.filter(user=user).update(is_verified=True, admin_verified_at=timezone.now(), admin_verified_by=request.user)
        return redirect('bo_accounts')

from django.core.mail import send_mail
from notifications.models import Notification  # if you want in-app notifications too
from users.models import User
from documents.verification import VerificationDocument

def verify_account_upload(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    # Disable new uploads if a pending request exists
    if user.verification_documents.exists() and any(doc.status == 'pending' for doc in user.verification_documents.all()):
        messages.warning(request, "You already have a pending verification request.")
        return redirect("settings")

    if request.method == "POST":
        files = request.FILES.getlist("files")
        if len(files) < 2:
            messages.error(request, "Please upload at least 2 files to verify your account.")
            return redirect("settings")

        for f in files:
            VerificationDocument.objects.create(user=user, file=f, status='pending')

        messages.success(request, "Documents uploaded successfully. Awaiting admin verification.")

        # Notify admins via email and in-app notification
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            send_mail(
                subject="New Verification Request",
                message=f"{user.get_full_name()} has submitted documents for verification.",
                from_email="noreply@example.com",
                recipient_list=[admin.email],
                fail_silently=True,
            )

            # Optional in-app notification
            Notification.objects.create(
                user=admin,
                sender=user,
                message=f"{user.get_full_name()} submitted verification documents.",
                type="info",
                url="/admin/users/view-verification/"  # link to admin view
            )

        return redirect("settings")

    return redirect("settings")


#Profile Edit View
from .forms import ProfileEditForm

class ProfileEditView(UpdateView):
    model = User
    form_class = ProfileEditForm
    template_name = "users/profile_edit.html"
    context_object_name = "profile"

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'pk': self.object.pk})




class CustomLoginView(FormSubmissionMixin, LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    authentication_form = CustomLoginForm
    
    def get_success_url(self) -> str:
        return reverse_lazy('dashboard')
    
class CustomRegisterView(FormSubmissionMixin, CreateView):
    template_name = 'users/register.html'
    redirect_authenticated_user = True
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('dashboard')

    def post(self, request, *args, **kwargs):
        print("=== POST METHOD CALLED ===")
        print(f"Is AJAX: {request.headers.get('X-Requested-With') == 'XMLHttpRequest'}")
        print(f"POST data: {dict(request.POST)}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        print("=== FORM_VALID CALLED ===")
        user = form.save(commit=False)
        user.is_verified = False
        user.save()

        user.generate_secure_otp_code()
        print(f"[DEBUG] Verification code for {user.username}: {user.verification_code}")

        self.request.session['pending_verification_user'] = user.id

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'verification_type': 'registration',
                'message': 'Registration successful! Please enter the verification code.',
                'show_verification': True,
                'masked_email': self.mask_email(user.email),
            })

        return super().form_valid(form)

    @staticmethod
    def mask_email(email):
        if '@' not in email:
            return email
        username, domain = email.split('@', 1)
        masked_username = username[:2] + '*' * (len(username) - 2) if len(username) > 2 else '*' * len(username)
        return f"{masked_username}@{domain}"

    

class VerifyUserView(View):
    def post(self, request, *args, **kwargs):
        user_id = request.session.get('pending_verification_user')
        if not user_id:
            return JsonResponse({'success': False, 'error': 'No pending verification'}, status=400)

        user = get_object_or_404(User, id=user_id)
        code = request.POST.get('code') or request.POST.get('verification_code', '')

        if not code or len(code) != 6:
            return JsonResponse({'success': False, 'error': 'Please enter a valid 6-digit code'}, status=400)

        if user.is_verification_code_valid(code):
            user.is_verified = True
            user.verification_code = None
            user.verification_code_expiration_date = None
            user.save()

            verification_type = request.POST.get('verification_type', '')

            if verification_type == 'reset_password':
                # For forgot password → reset flow
                request.session['reset_email'] = user.email
                del request.session['pending_verification_user']  # 🟢 clean session
                return JsonResponse({
                    'success': True,
                    'message': 'Verification successful!',
                    'redirect': reverse('reset_password')
                })
            else:
    # For normal registration flow
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                request.session.pop('pending_verification_user', None)
            return JsonResponse({
                    'success': True,
                    'message': 'Verification successful!',
                    'redirect': reverse('dashboard')
                })

        return JsonResponse({'success': False, 'error': 'Invalid or expired verification code'}, status=400)


class ResendCodeView(View):
    """Handles resending OTP"""

    def post(self, request, *args, **kwargs):
        user_id = request.session.get('pending_verification_user')
        if not user_id:
            return JsonResponse({'success': False, 'error': 'No pending verification'}, status=400)

        user = get_object_or_404(User, id=user_id)
        user.generate_secure_otp_code()

        # ✅ log it to terminal
        print(f"[DEBUG] Resent verification code for {user.username}: {user.verification_code}")

        return JsonResponse({
            'success': True,
            'message': 'Verification code resent!'
        })

# ---------------------- FUNCTION BASED VIEWS --------------------------- #    

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect("/")

def check_email_exists(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            if get_user_model().objects.filter(email=email).exists():
                return HttpResponse('<span style="color: red;">This email already exists</span>')
            else:
                return HttpResponse('<span style="color: green;">Email is available</span>')
    return HttpResponse("")

def check_password_strength(request):
    password = request.POST.get('password1', "")
    try:
        validate_password(password)
        html = '<span id="message-success" style="color: green;">Strong password</span>'
        response = HttpResponse(html)
        response['HX-Trigger'] = 'passwordValid'
        return response
    except ValidationError as e:
        error_spans = "".join(
            f'<span id="message-error" style="color:red; display:block;">{msg}</span>'
            for msg in e.messages
        )
        response = HttpResponse(error_spans)
        response['HX-Trigger'] = 'passwordInvalid'
        return response
    
def check_passwords_match(request):
    pass