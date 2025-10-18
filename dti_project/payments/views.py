
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
from documents.models import (
    SalesPromotionPermitApplication,
    OrderOfPayment,
)
from .forms import GCashPaymentForm

def payment_page(request, oop_id):
    """
    Display payment page for a specific OrderOfPayment.
    Only allows payment if an OOP exists.
    """
    oop = get_object_or_404(OrderOfPayment, pk=oop_id)
    sppa = oop.sales_promotion_permit_application

    # SPPA info for display
    business_name = sppa.sponsor_name
    scope = sppa.coverage
    registration_type = "Sales Promotion Permit"
    transaction_type = "Application"
    applicant_name = sppa.sponsor_authorized_rep

    # Calculate total amount
    remark_fields = [
        "discount_amount", "premium_amount", "raffle_amount",
        "contest_amount", "redemption_amount", "games_amount",
        "beauty_contest_amount", "home_solicitation_amount",
        "amendments_amount"
    ]
    subtotal = sum(getattr(oop, f, 0) for f in remark_fields)
    doc_stamp_fee = oop.doc_stamp_amount or 0
    total_amount = subtotal + doc_stamp_fee

    context = {
        "business_name": business_name,
        "scope": scope,
        "registration_type": registration_type,
        "transaction_type": transaction_type,
        "applicant_name": applicant_name,
        "citizenship": "Filipino",
        "processing_fee": subtotal,
        "doc_stamp_fee": doc_stamp_fee,
        "total_amount": total_amount,
    }

    return render(request, "payments/payment-page.html", context)

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
