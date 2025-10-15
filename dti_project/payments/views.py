from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import GCashPaymentForm
from documents.models import ServiceRepairAccreditationApplication
from documents.models import SalesPromotionPermitApplication
from decimal import Decimal
from documents.models import OrderOfPayment

def payment_page(request, document_type, document_id):
    """
    Display payment page for a document.
    Only allows payment if an Order of Payment (OOP) has been created by admin.
    """

    # Fetch the document
    if document_type == "sales-promo":
        doc = get_object_or_404(SalesPromotionPermitApplication, pk=document_id)
        business_name = doc.sponsor_name
        scope = doc.coverage
        registration_type = "Sales Promotion Permit"
        transaction_type = "Application"
        applicant_name = doc.sponsor_authorized_rep

    elif document_type == "service-repair":
        doc = get_object_or_404(ServiceRepairAccreditationApplication, pk=document_id)
        business_name = doc.name_of_business
        scope = doc.region
        registration_type = doc.form_of_organization
        transaction_type = doc.application_type
        applicant_name = f"{doc.first_name} {doc.last_name}"

    else:
        messages.error(request, "Invalid document type.")
        return redirect("dashboard")

    # Fetch the existing Order of Payment created by admin
    try:
        oop = OrderOfPayment.objects.get(user=request.user, name=business_name)
    except OrderOfPayment.DoesNotExist:
        messages.error(request, "The Order of Payment has not been created yet. Please contact the admin.")
        return redirect("dashboard")
    except OrderOfPayment.MultipleObjectsReturned:
        messages.error(request, "Multiple Orders of Payment found. Please contact the admin.")
        return redirect("dashboard")

    # Fees
    processing_fee = Decimal('500.00')
    doc_stamp_fee = Decimal(oop.doc_stamp_amount) if oop.doc_stamp_amount else Decimal('0.00')
    total_amount = processing_fee + doc_stamp_fee

    context = {
        "business_name": business_name,
        "scope": scope,
        "registration_type": registration_type,
        "transaction_type": transaction_type,
        "applicant_name": applicant_name,
        "citizenship": "Filipino",
        "processing_fee": processing_fee,
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
