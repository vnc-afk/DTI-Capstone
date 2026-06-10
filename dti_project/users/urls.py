from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('sign-in/', views.CustomLoginView.as_view(), name="sign-in"),
    path('register/', views.CustomRegisterView.as_view(), name="register"),
    path('verify-user/', views.VerifyUserView.as_view(), name='verify-user'),
    path('resend-code/', views.ResendCodeView.as_view(), name='resend-code'),
    path('logout/', views.logout, name="logout"),

    # Profile Detail View
    path('profile/<int:pk>/', views.ProfileDetailView.as_view(), name='profile'),

    # Profile Edit View
    path("settings/<int:pk>/profile-edit/", views.ProfileEditView.as_view(), name="profile_edit"),
    # Settings page
    path('settings/', views.SettingsView.as_view(), name='settings'),
    
    #Account pages
    path('staff-accounts/', views.StaffListView.as_view(), name="staff_accounts"),
    path('business-owner-accounts/', views.BusinessOwnerListView.as_view(), name="bo_accounts"),

    # Add Staff Account
    path('staff-accounts/add/', views.add_staff, name="add_staff"),
    path('staff-accounts/delete/<int:user_id>/', views.delete_new_staff, name='delete_new_staff'),

    #Forgot Password
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),

    # Verify Account (Unverified Owner)
    path('settings/verify-account/<int:pk>/', views.VerifyUserView.as_view(), name='verify_account'),
    path('verify-user/<int:user_id>/', views.verify_user, name='verify_user'),
    path('settings/verify-account/<int:user_id>/upload/', views.verify_account_upload, name='verify_account_upload'),





]

htmxpatterns = [
    path('check_email_exists', views.check_email_exists, name="check-email-exists"),
    path('check_password_strength', views.check_password_strength, name='check-password-strength')
]

urlpatterns += htmxpatterns