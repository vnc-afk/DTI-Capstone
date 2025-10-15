from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import GCashPaymentForm
from documents.models import ServiceRepairAccreditationApplication


def payment_page(request):
    user = request.user  # Current logged-in user

    # Get the most recent accreditation for this user
    accreditation = get_object_or_404(ServiceRepairAccreditationApplication, user=user)

    if request.method == 'POST':
        if 'proceed' in request.POST:
            payment_method = request.POST.get('payment_method')
            total = 530  # Or calculate dynamically

            if payment_method == 'gcash':
                request.session['total'] = total
                return redirect('gcash_payment')  # Redirect to GCash page

            elif payment_method == 'over-the-counter':
                messages.info(request, "Over-the-counter payment not implemented yet.")
                return redirect('payment_page')

        elif 'resume' in request.POST:
            messages.info(request, "You can resume later!")
            return redirect('payment_page')

    # GET request: render page with accreditation data
    return render(request, 'payments/payment-page.html', {"accreditation": accreditation})


def gcash_payment(request):
    total = request.session.get('total', 0)
    form = GCashPaymentForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        reference_number = form.cleaned_data['reference_number']
        proof = form.cleaned_data['proof']

        messages.success(request, "Payment submitted successfully!")
        return redirect('gcash_success')

    return render(request, 'payments/gcash_payment.html', {'total': total, 'form': form})


def gcash_success(request):
    return render(request, 'payments/gcash_success.html')
