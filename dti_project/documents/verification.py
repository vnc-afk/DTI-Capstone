# documents/verification.py

from django.db import models
from users.models import User  # import your User model

class VerificationDocument(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="verification_documents"
    )
    file = models.FileField(upload_to="verification_documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    def __str__(self):
        return f"{self.user.email} - {self.file.name}"
