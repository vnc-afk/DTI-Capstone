from datetime import timedelta
import secrets
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.

class User(AbstractUser):
    class Roles(models.TextChoices):
        UNVERIFIED_OWNER = "unverified_owner", "Unverfied Owner"
        BUSINESS_OWNER = "business_owner", "Business Owner"
        ADMIN = "admin", "Admin"
        COLLECTION_AGENT = "collection_agent", "Collection Agent"
        ALT_COLLECTION_AGENT = "alt_collection_agent", "Alternative Collection Agent"
        AUTHORIZED_OFFICIAL = "authorized_official", "Authorized Official"

    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        default='profile_pictures/default-avatar-icon.jpg',
        blank=True
    )
    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.UNVERIFIED_OWNER
    )
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    verification_code_expiration_date = models.DateTimeField(blank=True, null=True)

    default_address = models.CharField(max_length=255, blank=True, null=True)
    default_phone = models.CharField(max_length=11, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)

    dti_office = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Only applicable if the user is a collection agent."
    )
    official_designation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Only applicable if the user is a collection agent."
    )

    birthday = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse("profile", args=[self.pk])
    
    def generate_secure_otp_code(self):
        """Generate cryptographically secure 6-digit OTP and save to user"""
        code = ''.join(secrets.choice('0123456789') for _ in range(6))
        self.verification_code = code
        self.verification_code_expiration_date = timezone.now() + timedelta(minutes=30)  # expires in 30 minutes
        self.save(update_fields=["verification_code", "verification_code_expiration_date"])
        return code
    
    def is_verification_code_valid(self, code):
        """Check if verification code is valid and not expired"""
        return (
            self.verification_code == code and
            self.verification_code_expiration_date and
            timezone.now() < self.verification_code_expiration_date  # Fixed: now() and < instead of >
        )

    def get_full_name(self):
        parts = [self.first_name]
        if getattr(self, 'middle_name', None):  # safe check
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join(filter(None, parts))
    
    def new_notifications(self):
        return self.notifications.filter(is_read=False)
    
    def save(self, *args, **kwargs):
        """
        Automatically fill DTI office and official designation
        if the user is a collection agent.
        """
        if self.role == self.Roles.COLLECTION_AGENT:
            # Apply defaults only if empty
            if not self.dti_office:
                self.dti_office = "DTI Albay Provincial Office"
            if not self.official_designation:
                self.official_designation = "Special Collecting Officer"
        else:
            # Wipe these fields for non-collection agents
            self.dti_office = None
            self.official_designation = None

        # Force superusers to always be admin
        if self.is_superuser:
            self.role = self.Roles.ADMIN
            
        super().save(*args, **kwargs)

class ActivityLog(models.Model):
    class ActionType(models.TextChoices):
        # Authentication Events
        LOGIN = "login", "Login"
        LOGOUT = "logout", "Logout"
        LOGIN_FAILED = "login_failed", "Failed Login"
        
        # Page Visits
        PAGE_VIEW = "page_view", "Page Visit"
        
        # CRUD Actions
        CREATE = "create", "Created"
        UPDATE = "update", "Updated"
        DELETE = "delete", "Deleted"
        UPLOAD = "upload", "Uploaded File"
        
        # Payment Activities
        PAYMENT_INITIATED = "payment_initiated", "Payment Initiated"
        PAYMENT_VERIFIED = "payment_verified", "Payment Verified"
        PAYMENT_FAILED = "payment_failed", "Payment Failed"
        REFUND_INITIATED = "refund_initiated", "Refund Initiated"
        
        # Approval Workflow
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        SUBMITTED = "submitted", "Submitted"
        
        # System Events
        SESSION_EXPIRED = "session_expired", "Session Expired"
        PASSWORD_CHANGED = "password_changed", "Password Changed"
        EMAIL_CHANGED = "email_changed", "Email Changed"

    class Visibility(models.TextChoices):
        PRIVATE = "private", "Private (User only)"
        PUBLIC = "public", "All users"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="activity_logs")
    role = models.CharField(max_length=20, blank=True, null=True)
    action_type = models.CharField(max_length=30, choices=ActionType.choices)
    action = models.CharField(max_length=500)  # Human-readable description
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Visibility control
    visibility = models.CharField(max_length=20, choices=Visibility.choices, default=Visibility.PRIVATE)
    
    # Object reference
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.CharField(max_length=255, null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")
    
    # Network info
    ip_address = models.CharField(max_length=45, null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Additional data
    extra = models.JSONField(null=True, blank=True, default=dict)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "-timestamp"]),
            models.Index(fields=["action_type", "-timestamp"]),
        ]

    def __str__(self):
        who = self.user.get_full_name() if self.user else "System"
        return f"{self.timestamp:%Y-%m-%d %H:%M} — {self.action}"

    @classmethod
    def get_visible_logs(cls, viewing_user):
        """Get activity logs visible to the viewing user based on their role"""
        from users.models import User
        
        if viewing_user.role == User.Roles.ADMIN:
            # Admins see everything
            return cls.objects.all().order_by('-timestamp')
        else:
            # Business owners and collection agents see nothing
            return cls.objects.none()
