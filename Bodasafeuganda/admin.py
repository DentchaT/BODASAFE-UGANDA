#from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Institution, SecretaryProfile, Advert, RequiredDocument, Submission, Payment

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'phone_number', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone_number')}),
    )

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'created_at')
    search_fields = ('name', 'district')

@admin.register(SecretaryProfile)
class SecretaryProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution')

class RequiredDocumentInline(admin.TabularInline):
    model = RequiredDocument
    extra = 1

@admin.register(Advert)
class AdvertAdmin(admin.ModelAdmin):
    list_display = ('title', 'institution', 'service_fee', 'deadline')
    inlines = [RequiredDocumentInline]

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'advert', 'required_document', 'status', 'uploaded_at')
    list_filter = ('status',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'advert', 'amount', 'status', 'created_at')