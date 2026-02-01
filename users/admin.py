from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Users, UserPaymentAccount, Roles

class CustomUserAdmin(UserAdmin):
    list_display = (
        "email",
        "username",
        "full_name",
        "firebase_uid",
        "is_staff",
        "total_donations",
        "total_impact",
    )
    search_fields = ("email", "username", "full_name", "firebase_uid")
    readonly_fields = ("total_donations", "total_impact", "firebase_uid")

    fieldsets = UserAdmin.fieldsets + (
        (
            "Extra Info",
            {
                "fields": (
                    "full_name",
                    "phone_number",
                    "firebase_uid",
                    "role",
                    "profile_image",
                    "bio",
                    "address",
                    "default_donation_account",
                )
            },
        ),
        (
            "Analytics",
            {"fields": ("total_donations", "total_impact")},
        ),
    )

class UserPaymentAccountAdmin(admin.ModelAdmin):
    list_display = ("user", "account_type", "provider", "account_number", "is_default")
    list_filter = ("account_type", "provider", "is_default")
    search_fields = ("user__email", "account_number")

admin.site.register(Users, CustomUserAdmin)
admin.site.register(UserPaymentAccount, UserPaymentAccountAdmin)
admin.site.register(Roles)
