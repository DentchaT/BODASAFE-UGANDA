from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, SecretaryProfile, Institution, Advert, RequiredDocument, Submission

# Applicant Registration Form
class ApplicantRegistrationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15, required=True)
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'phone_number')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'applicant'
        if commit:
            user.save()
        return user


# Secretary Registration Form
class SecretaryRegistrationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15, required=True)
    email = forms.EmailField(required=True)
    institution = forms.ModelChoiceProvider if False else forms.ModelChoiceField(
        queryset=Institution.objects.all(), 
        empty_label="Select your Institution", 
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'phone_number')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'secretary'
        if commit:
            user.save()
            SecretaryProfile.objects.create(
                user=user,
                institution=self.cleaned_data['institution']
            )
        return user


# Form for uploading a document
class DocumentSubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('file',)

class AdvertForm(forms.ModelForm):
    class Meta:
        model = Advert
        fields = ['title', 'description', 'deadline', 'service_fee']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-input'}),
        }

class RequiredDocumentForm(forms.ModelForm):
    class Meta:
        model = RequiredDocument
        fields = ['name', 'description']

class PaymentForm(forms.Form):
    PROVIDER_CHOICES = [
        ('MTN', 'MTN Mobile Money'),
        ('Airtel', 'Airtel Money'),
    ]
    phone_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., 0771234567'}))
    provider = forms.ChoiceField(choices=PROVIDER_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))