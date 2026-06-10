from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.db.models import Value, F, Q
from django.contrib import messages

class OwnershipDraftMixin:
    """
    Ensures that only the owning user can edit an object,
    and only if the object is still in draft status.
    """

    draft_only = True  # set to False if some forms can bypass draft restriction

    def post(self, request, *args, **kwargs):
        obj = self.get_object()

        # Ownership check
        if hasattr(obj, "user") and obj.user != request.user:
            messages.error(request, "You cannot edit this item.")
            return redirect("/")

        # Status check (optional toggle)
        if self.draft_only and hasattr(obj, "status") and obj.status != "draft":
            messages.error(request, "You can only edit drafts.")
            return redirect("/")

        return super().post(request, *args, **kwargs)
    
class UserRoleMixin:
    @staticmethod
    def get_queryset_or_all(model, user):
        # Collection agents (main + alt) → same access
        if user.role in ["collection_agent", "alt_collection_agent"]:
            # Access drafts owned by user + all non-draft objects
            qs = model.objects.filter(Q(status="draft", user=user) | ~Q(status="draft"))
        # Authorized officials → same access as business owners
        elif user.role == "authorized_official" or user.role == 'business_owner':
            qs = model.objects.filter(user=user)
        # Admin → all access
        elif user.role == 'admin':
            qs = model.objects.all()
        else:
            qs = model.objects.none()  # fallback for unknown roles
        return qs.only("pk", "id")  # Add other fields your templates need
    
    @staticmethod
    def get_count_or_all(model, user):
        if user.role in ["collection_agent", "alt_collection_agent", "authorized_official"]:
            return model.objects.filter(Q(status="draft", user=user) | ~Q(status="draft")).count()
        elif user.role == "authorized_official" or user.role == 'business_owner':
            return model.objects.filter(user=user).count()
        elif user.role == 'admin':
            return model.objects.count()
        else:
            return model.objects.filter(user=user).count()


class PreventAdminFormPostRequestMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.role == 'admin':
            messages.error(request, "Admins are not allowed to access this page.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        return super().dispatch(request, *args, **kwargs)
    
class RoleFormPageRestrictionMixin:
    allowed_roles = []  # Define allowed roles per view
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in self.allowed_roles:
            messages.error(request, f"{request.user.role.replace('_', ' ').title()}s are not allowed to access this page.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        return super().dispatch(request, *args, **kwargs)