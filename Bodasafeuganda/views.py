from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import ApplicantRegistrationForm, SecretaryRegistrationForm, PaymentForm
from .models import Advert, Institution, Submission, RequiredDocument, Payment

def home(request):
    adverts = Advert.objects.all().order_by('-created_at')[:6]
    return render(request, 'core/home.html', {'adverts': adverts})

def register_applicant(request):
    if request.method == 'POST':
        form = ApplicantRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('applicant_dashboard')
    else:
        form = ApplicantRegistrationForm()
    return render(request, 'core/register_applicant.html', {'form': form})

def register_secretary(request):
    if request.method == 'POST':
        form = SecretaryRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('secretary_dashboard')
    else:
        form = SecretaryRegistrationForm()
    return render(request, 'core/register_secretary.html', {'form': form})

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.role == 'secretary':
                return redirect('secretary_dashboard')
            return redirect('applicant_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

@login_required
def custom_logout(request):
    logout(request)
    return redirect('home')

#---------------------------SECRETARY VIEWS---------------------------------

from .models import Advert, RequiredDocument, Submission, SecretaryProfile
from django.forms import inlineformset_factory
from .forms import AdvertForm, RequiredDocumentForm
@login_required
def secretary_dashboard(request):
    if request.user.role != 'secretary':
        return redirect('applicant_dashboard')
    
    try:
        profile = request.user.secretary_profile
        adverts = Advert.objects.filter(created_by=profile).order_by('-created_at')
    except SecretaryProfile.DoesNotExist:
        adverts = []
        profile = None

    return render(request, 'core/secretary_dashboard.html', {
        'profile': profile,
        'adverts': adverts
    })

@login_required
def create_advert(request):
    if request.user.role != 'secretary':
        return redirect('home')

    profile = request.user.secretary_profile
    RequiredDocFormSet = inlineformset_factory(
        Advert, RequiredDocument, fields=('name', 'description'), extra=3, can_delete=False
    )

    if request.method == 'POST':
        form = AdvertForm(request.POST)
        formset = RequiredDocFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            advert = form.save(commit=False)
            advert.institution = profile.institution
            advert.created_by = profile
            advert.save()
            formset.instance = advert
            formset.save()
            return redirect('secretary_dashboard')
    else:
        form = AdvertForm()
        formset = RequiredDocFormSet()

    return render(request, 'core/create_advert.html', {
        'form': form,
        'formset': formset
    })

@login_required
def review_submissions(request, advert_id):
    if request.user.role != 'secretary':
        return redirect('home')

    advert = get_object_or_404(Advert, id=advert_id)
    submissions = Submission.objects.filter(advert=advert).select_related('applicant', 'required_document')

    if request.method == 'POST':
        submission_id = request.POST.get('submission_id')
        new_status = request.POST.get('status')
        comment = request.POST.get('comment', '')

        sub = get_object_or_404(Submission, id=submission_id)
        sub.status = new_status
        sub.secretary_comment = comment
        sub.save()
        return redirect('review_submissions', advert_id=advert.id)

    return render(request, 'core/review_submissions.html', {
        'advert': advert,
        'submissions': submissions
    })

#---------------APPLICANT VIEWS-----------------

from django.db.models import Q

@login_required
def applicant_dashboard(request):
    if request.user.role != 'applicant':
        return redirect('secretary_dashboard')

    query = request.GET.get('q', '')
    adverts = Advert.objects.all()
    if query:
        adverts = adverts.filter(
            Q(title__icontains=query) | 
            Q(institution__name__icontains=query) |
            Q(institution__district__icontains=query)
        )

    # Calculate submission status for each advert for the current applicant
    user_submissions = Submission.objects.filter(applicant=request.user)
    submitted_doc_ids = set(user_submissions.values_list('required_document_id', flat=True))

    return render(request, 'core/applicant_dashboard.html', {
        'adverts': adverts,
        'query': query,
        'submitted_doc_ids': submitted_doc_ids
    })

@login_required
def advert_detail(request, advert_id):
    advert = get_object_or_404(Advert, id=advert_id)
    required_docs = advert.required_documents.all()
    payment_completed = Payment.objects.filter(applicant=request.user, advert=advert, status='completed').exists()
    
    # Fetch existing user submissions for this advert
    user_subs = Submission.objects.filter(applicant=request.user, advert=advert)
    user_subs_dict = {sub.required_document_id: sub for sub in user_subs}

    total_docs = required_docs.count()
    uploaded_count = user_subs.count()
    is_complete = total_docs > 0 and uploaded_count == total_docs

    if request.method == 'POST':
        doc_id = request.POST.get('document_id')
        uploaded_file = request.FILES.get('document_file')
        
        if doc_id and uploaded_file:
            req_doc = get_object_or_404(RequiredDocument, id=doc_id)
            Submission.objects.update_or_create(
                applicant=request.user,
                advert=advert,
                required_document=req_doc,
                defaults={'file': uploaded_file, 'status': 'pending'}
            )
            return redirect('advert_detail', advert_id=advert.id)

    # Build detailed list with upload status and CSS class
    doc_status_list = []
    for doc in required_docs:
        sub = user_subs_dict.get(doc.id)
        if sub:
            if sub.status == 'approved':
                badge_color = 'bg-green-100 text-green-800 border-green-400'
                status_text = 'Approved'
            elif sub.status == 'rejected':
                badge_color = 'bg-red-100 text-red-800 border-red-400'
                status_text = 'Rejected - Re-upload needed'
            else:
                badge_color = 'bg-blue-100 text-blue-800 border-blue-400'
                status_text = 'Uploaded (Pending Review)'
        else:
            badge_color = 'bg-gray-100 text-gray-700 border-gray-300'
            status_text = 'Missing'

        doc_status_list.append({
            'doc': doc,
            'submission': sub,
            'badge_color': badge_color,
            'status_text': status_text,
            'is_uploaded': sub is not None
        })

    return render(request, 'core/advert_detail.html', {
        'advert': advert,
        'doc_status_list': doc_status_list,
        'uploaded_count': uploaded_count,
        'total_docs': total_docs,
        'is_complete': is_complete
    })

#------------PAYMENT VIEWS----------------
import uuid

@login_required
def make_payment(request, advert_id):
    if request.user.role != 'applicant':
        return redirect('home')

    advert = get_object_or_404(Advert, id=advert_id)
    
    # Check if payment is already completed
    existing_payment = Payment.objects.filter(applicant=request.user, advert=advert, status='completed').first()
    if existing_payment:
        return redirect('advert_detail', advert_id=advert.id)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            provider = form.cleaned_data['provider']
            
            # Simulate a successful Mobile Money API transaction reference
            tx_ref = f"MOMO-{uuid.uuid4().hex[:8].upper()}"
            
            Payment.objects.create(
                applicant=request.user,
                advert=advert,
                amount=advert.service_fee,
                status='completed',  # Simulated success
                transaction_reference=f"{provider}-{phone}-{tx_ref}"
            )
            return redirect('advert_detail', advert_id=advert.id)
    else:
        form = PaymentForm(initial={'phone_number': request.user.phone_number})

    return render(request, 'core/make_payment.html', {
        'advert': advert,
        'form': form
    })
