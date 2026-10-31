from django.db import models
from cloudinary.models import CloudinaryField

# Create your models here.

# 1. Custom User Model supporting Roles
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('secretary', 'Secretary'),
        ('applicant', 'Applicant'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='applicant')
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


# 2. Institution Model
#class Institution(models.Name = models.CharField(max_length=255, unique=True)
class Institution(models.Model):
    name = models.CharField(max_length=255, unique=True)
    district = models.CharField(max_length=100) # e.g., Mbarara, Kampala
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.district}"


# 3. Secretary Profile (Links a Secretary user to an Institution)
class SecretaryProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='secretary_profile')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='secretaries')
    
    def __str__(self):
        return f"{self.user.username} - {self.institution.name}"


# 4. Advertisement / Call for Application
class Advert(models.Model):
    title = models.CharField(max_length=255) # e.g., "Dental Surgeon Job Vacancy 2026"
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='adverts')
    created_by = models.ForeignKey(SecretaryProfile, on_delete=models.CASCADE)
    description = models.TextField()
    deadline = models.DateField()
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, help_text="Fee paid to secretary for processing")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# 5. Required Documents for a Specific Advert
class RequiredDocument(models.Model):
    advert = models.ForeignKey(Advert, on_delete=models.CASCADE, related_name='required_documents')
    name = models.CharField(max_length=255) # e.g., "Degree Certificate", "Annual Practicing License"
    description = models.TextField(blank=True, help_text="Specific instructions like 'PDF format under 2MB'")

    def __str__(self):
        return f"{self.name} (for {self.advert.title})"


# 6. Applicant Submissions
class Submission(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected - Re-upload Needed'),
    )
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    advert = models.ForeignKey(Advert, on_delete=models.CASCADE, related_name='applications')
    required_document = models.ForeignKey(RequiredDocument, on_delete=models.CASCADE)
    file = CloudinaryField('file',folder='applicant_documents/',resource_type='auto',blank=True, null=True)#models.FileField(upload_to='applicant_documents/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    secretary_comment = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant.username} - {self.required_document.name} [{self.status}]"


# 7. Payment Tracking Model
class Payment(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    advert = models.ForeignKey(Advert, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment by {self.applicant.username} - {self.amount} ({self.status})"