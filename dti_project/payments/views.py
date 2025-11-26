from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from notifications.utils import send_user_notification
import random
import string
import requests
import base64
import datetime
from io import BytesIO
from decimal import Decimal
from users.models import User
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from notifications.models import Notification
from django.contrib.contenttypes.models import ContentType
from documents.models import SalesPromotionPermitApplication, OrderOfPayment, ServiceRepairAccreditationApplication
from documents.models.collection_models import CollectionReport, CollectionReportItem
from django.utils import timezone


def _get_doc_objects(doc_type, pk):
    """
    Returns a dict with keys dependent on doc_type:
    - 'type' : 'oop' or 'service'
    - 'oop', 'sppa' for Sales Promotion
    - 'sra' for Service Repair
    """
    if doc_type == "oop":
        oop = get_object_or_404(OrderOfPayment, pk=pk)
        sppa = oop.sales_promotion_permit_application
        total_amount = oop.total_amount or oop.calculate_total()
        processing_fee = total_amount - (oop.doc_stamp_amount or Decimal('0.00'))
        return {
            "type": "oop",
            "oop": oop,
            "sppa": sppa,
            "user": sppa.user,
            "total_amount": total_amount,
            "processing_fee": processing_fee,
            "doc_stamp_fee": oop.doc_stamp_amount or Decimal('0.00'),
            "display_name": "Sales Promotion Permit",
        }
    elif doc_type == "service":
        sra = get_object_or_404(ServiceRepairAccreditationApplication, pk=pk)
        total_amount = sra.total_amount or sra.calculate_fee()
        return {
            "type": "service",
            "sra": sra,
            "user": sra.user,
            "total_amount": total_amount,
            "processing_fee": total_amount,
            "doc_stamp_fee": Decimal('0.00'),
            "display_name": "Service Repair Accreditation",
        }
    else:
        raise ValueError("Unknown document type")

def payment_page(request, doc_type, pk):
    """
    Generic payment page for both OOP (doc_type='oop') and Service Repair (doc_type='service').
    """
    try:
        ctx = _get_doc_objects(doc_type, pk)
    except ValueError:
        messages.error(request, "Invalid payment target.")
        return redirect('documents-list')

    context = {
        "oop": ctx.get("oop"),
        "application": ctx.get("sra") or ctx.get("sppa"),
        "business_name": (ctx.get("sppa").sponsor_name if ctx.get("sppa") else getattr(ctx.get("sra"), "name_of_business", "")),
        "scope": (ctx.get("sppa").coverage if ctx.get("sppa") else getattr(ctx.get("sra"), "category", "")),
        "registration_type": ctx["display_name"],
        "transaction_type": "Application",
        "applicant_name": (ctx.get("sppa").sponsor_authorized_rep if ctx.get("sppa") else f"{ctx.get('sra').title} {ctx.get('sra').first_name} {ctx.get('sra').last_name}"),
        "citizenship": "Filipino",
        "processing_fee": ctx["processing_fee"],
        "doc_stamp_fee": ctx["doc_stamp_fee"],
        "total_amount": ctx["total_amount"],
    }

    if request.method == "POST" and "proceed" in request.POST:
        payment_method = request.POST.get("payment_method")
        if payment_method == "gcash":
            key = base64.b64encode(settings.PAYMONGO_SECRET_KEY.encode()).decode()
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": f"Basic {key}",
            }

            data = {
                "data": {
                    "attributes": {
                        "amount": int(ctx["total_amount"] * 100),  # centavos
                        "currency": "PHP",
                        "type": "gcash",
                        "redirect": {
                            "success": request.build_absolute_uri(reverse("payment-success", args=[doc_type, pk])),
                            "failed": request.build_absolute_uri(reverse("payment-failed")),
                        }
                    }
                }
            }

            response = requests.post("https://api.paymongo.com/v1/sources", headers=headers, json=data)
            result = response.json()

            if "data" in result:
                checkout_url = result["data"]["attributes"]["redirect"]["checkout_url"]
                return redirect(checkout_url)
            else:
                messages.error(request, "Failed to initialize payment. Please try again.")

    return render(request, "payments/payment-page.html", context)

def payment_success(request, doc_type, pk):
    """
    Generic payment success callback. Marks Paid, logs to collection report,
    and notifies admins + owner.
    """


    try:
        ctx = _get_doc_objects(doc_type, pk)
    except ValueError:
        messages.error(request, "Invalid payment target.")
        return redirect('documents-list')

    # ----------------------------------------------------------
    # Mark as PAID (but not VERIFIED)
    # ----------------------------------------------------------
    if ctx["type"] == "oop":
        oop = ctx["oop"]
        if oop.payment_status != OrderOfPayment.PaymentStatus.VERIFIED:
            oop.payment_status = OrderOfPayment.PaymentStatus.PAID
            oop.save()
        target_obj = oop
        owner = ctx["user"]
        display_id = oop.pk

    else:
        sra = ctx["sra"]
        if sra.payment_status != ServiceRepairAccreditationApplication.PaymentStatus.VERIFIED:
            sra.payment_status = ServiceRepairAccreditationApplication.PaymentStatus.PAID
            sra.save()
        target_obj = sra
        owner = ctx["user"]
        display_id = sra.pk

    # ----------------------------------------------------------
    #  CREATE COLLECTION REPORT ITEM AFTER PAYMENT SUCCESS  
    # ----------------------------------------------------------
    today = timezone.now().date()

    # 1️⃣ Get or create today's collection report
    report, created = CollectionReport.objects.get_or_create(
        report_collection_date=today,
        defaults={
            "dti_office": "DTI Office",  # optional default field
            "report_no": f"RPT-{today.strftime('%Y%m%d')}",
        }
    )

    # 2️⃣ Prepare values for CollectionReportItem
    payor = owner.get_full_name()
    particulars = ctx["display_name"]  # "Sales Promotion Permit" OR "Service Repair Accreditation"
    amount = ctx["total_amount"]
    stamp_tax = ctx["doc_stamp_fee"] or 0

    # 3️⃣ Create the CollectionReportItem
    item = CollectionReportItem.objects.create(
        payor=payor,
        particulars=particulars,
        amount=amount,
        stamp_tax=stamp_tax,
    )

    # 4️⃣ Add item to report
    report.report_items.add(item)
    report.save()

    # ----------------------------------------------------------
    # SEND NOTIFICATIONS
    # ----------------------------------------------------------
    admins = User.objects.filter(role__in=["admin", "collection_agent"])
    for admin in admins:
        notification = Notification.objects.create(
            user=admin,
            sender=request.user,
            message=f"{request.user.get_full_name()} has successfully paid for {ctx['display_name']} #{display_id}.",
            type="info",
            content_type=ContentType.objects.get_for_model(target_obj),
            object_id=display_id,
        )
        send_user_notification(admin.id, notification)

    notification = Notification.objects.create(
        user=owner,
        sender=request.user,
        message=f"Your payment for {ctx['display_name']} #{display_id} was successful and is now pending verification.",
        type="info",
        content_type=ContentType.objects.get_for_model(target_obj),
        object_id=display_id,
    )
    send_user_notification(owner.id, notification)

    # ----------------------------------------------------------
    # RETURN SUCCESS PAGE
    # ----------------------------------------------------------
    return render(request, "payments/payment_success.html", {"application": target_obj})


def payment_failed(request):
    messages.error(request, "Payment failed or was canceled. Please try again.")
    return render(request, "payments/payment_failed.html")

@login_required
def verify_payment(request, doc_type, pk):
    try:
        ctx = _get_doc_objects(doc_type, pk)
    except ValueError:
        messages.error(request, "Invalid target for verification.")
        return redirect('documents-list')

    if request.user.role not in ["admin", "collection_agent"]:
        messages.error(request, "You do not have permission to verify payments.")
        return redirect('documents-list')

    if ctx["type"] == "oop":
        oop = ctx["oop"]
        if oop.payment_status == OrderOfPayment.PaymentStatus.PAID:
            oop.payment_status = OrderOfPayment.PaymentStatus.VERIFIED
            oop.save()
            target_user = ctx["user"]
            notification = Notification.objects.create(
                user=target_user,
                sender=request.user,
                message=f"Your payment for OOP #{oop.pk} has been verified! You can now download your official receipt.",
                type="approved",
                content_type=ContentType.objects.get_for_model(oop),
                object_id=oop.pk,
            )
            send_user_notification(target_user.id, notification)
        else:
            messages.warning(request, "Payment must be marked as 'Paid' before verifying.")
    else:
        sra = ctx["sra"]
        if sra.payment_status == ServiceRepairAccreditationApplication.PaymentStatus.PAID:
            sra.payment_status = ServiceRepairAccreditationApplication.PaymentStatus.VERIFIED
            if not sra.reference_code:
                sra.reference_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
                sra.acknowledgment_generated_at = timezone.now()
            sra.save()
            target_user = ctx["user"]
            notification = Notification.objects.create(
                user=target_user,
                sender=request.user,
                message=f"Your payment for Service Repair Accreditation #{sra.pk} has been verified! You can now download your official receipt.",
                type="approved",
                content_type=ContentType.objects.get_for_model(sra),
                object_id=sra.pk,
            )
            send_user_notification(target_user.id, notification)
        else:
            messages.warning(request, "Payment must be marked as 'Paid' before verifying.")

    return redirect('all-documents')

@login_required
def download_receipt(request, doc_type, pk):
    try:
        ctx = _get_doc_objects(doc_type, pk)
    except ValueError:
        messages.error(request, "Invalid receipt target.")
        return redirect('documents-list')

    if ctx["type"] == "oop":
        oop = ctx["oop"]
        if oop.payment_status != OrderOfPayment.PaymentStatus.VERIFIED:
            messages.warning(request, "Receipt is only available after verification.")
            return redirect('documents-list')

        sppa = ctx["sppa"]
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # HEADER
        p.setFont("Helvetica-Bold", 14)
        p.drawCentredString(width / 2, height - 70, "ACKNOWLEDGMENT RECEIPT")
        p.setFont("Helvetica", 9)
        p.drawCentredString(width / 2, height - 85, "(This serves as proof of online payment)")
        p.drawCentredString(width / 2, height - 97,
                            "An official receipt will be issued by the DTI Cashier or authorized payment partner.")

        # PAYMENT INFO
        p.setFont("Helvetica", 10)
        p.drawString(50, height - 130, f"Reference Code: {oop.reference_code or 'N/A'}")
        p.drawString(50, height - 160, f"Issue Date: {datetime.datetime.now().strftime('%d %B %Y, %I:%M %p')}")
        p.drawString(50, height - 175, f"Application Name: {sppa.sponsor_name}")
        p.drawString(50, height - 190, f"Authorized Representative: {sppa.sponsor_authorized_rep}")
        p.drawString(50, height - 205, f"Transaction Type: Sales Promotion Permit Application")

        # AMOUNTS
        y = height - 235
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, y, "Fee Descriptionasdasd")
        p.drawString(300, y, "Amount (₱)")
        p.line(50, y - 2, 550, y - 2)

        processing_fee = (oop.total_amount or 0) - (oop.doc_stamp_amount or 0)
        y -= 20
        p.setFont("Helvetica", 10)
        p.drawString(50, y, "Processing Fee")
        p.drawRightString(550, y, f"{processing_fee:,.2f}")

        y -= 15
        p.drawString(50, y, "Documentary Stamp Tax")
        p.drawRightString(550, y, f"{oop.doc_stamp_amount or 0:,.2f}")

        y -= 20
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, y, "TOTAL AMOUNT PAID")
        p.drawRightString(550, y, f"{oop.total_amount or 0:,.2f}")
        p.line(400, y - 2, 550, y - 2)

        # FOOTER
        y -= 40
        p.setFont("Helvetica", 10)
        p.drawString(50, y, f"Verified By: {request.user.get_full_name()}")
        p.drawString(50, y - 15, f"Date Verified: {datetime.datetime.now().strftime('%d %B %Y')}")

        p.setFont("Helvetica-Oblique", 8)
        p.setFillGray(0.3)
        footer = ("This acknowledgment receipt is system-generated for proof of online payment.\n"
                "The official DTI or LGU receipt will be issued by the authorized cashier or integrated payment gateway as per government policy.")
        p.drawCentredString(width / 2, 80, footer.split('\n')[0])
        p.drawCentredString(width / 2, 68, footer.split('\n')[1])

        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, content_type='application/pdf', as_attachment=False)

    else:
        sra = ctx["sra"]
        if sra.payment_status != ServiceRepairAccreditationApplication.PaymentStatus.VERIFIED:
            messages.warning(request, "Receipt is only available after verification.")
            return redirect('documents-list')

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        p.setFont("Helvetica-Bold", 14)
        p.drawCentredString(width / 2, height - 70, "ACKNOWLEDGMENT RECEIPT")
        p.setFont("Helvetica", 9)
        p.drawCentredString(width / 2, height - 85, "(This serves as proof of online payment)")

        p.setFont("Helvetica", 10)
        p.drawString(50, height - 130, f"Reference Code: {sra.reference_code or 'N/A'}")
        p.drawString(50, height - 160, f"Issue Date: {timezone.now().strftime('%d %B %Y, %I:%M %p')}")
        p.drawString(50, height - 175, f"Application Name: {sra.name_of_business}")
        p.drawString(50, height - 190, f"Authorized Representative: {sra.title} {sra.first_name} {sra.last_name}")
        p.drawString(50, height - 205, f"Transaction Type: Service Repair Accreditation Application")

        y = height - 235
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, y, "Fee Description")
        p.drawString(300, y, "Amount (₱)")
        p.line(50, y - 2, 550, y - 2)

        processing_fee = sra.total_amount or sra.calculate_fee()
        y -= 20
        p.setFont("Helvetica", 10)
        p.drawString(50, y, "Processing Fee")
        p.drawRightString(550, y, f"{processing_fee:,.2f}")

        y -= 20
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, y, "TOTAL AMOUNT PAID")
        p.drawRightString(550, y, f"{sra.total_amount or processing_fee:,.2f}")
        p.line(400, y - 2, 550, y - 2)

        y -= 40
        p.setFont("Helvetica", 10)
        p.drawString(50, y, f"Verified By: {request.user.get_full_name()}")
        p.drawString(50, y - 15, f"Date Verified: {timezone.now().strftime('%d %B %Y')}")

        p.setFont("Helvetica-Oblique", 8)
        p.setFillGray(0.3)
        footer = ("This acknowledgment receipt is system-generated for proof of online payment.\n"
                "The official DTI or LGU receipt will be issued by the authorized cashier or integrated payment gateway as per government policy.")
        p.drawCentredString(width / 2, 80, footer.split('\n')[0])
        p.drawCentredString(width / 2, 68, footer.split('\n')[1])

        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, content_type='application/pdf', as_attachment=False)
