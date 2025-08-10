from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.mail import send_mail, BadHeaderError
from django import forms

from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["name", "email", "phone", "choice", "date_needed", "details"]
        widgets = {
            "date_needed": forms.DateInput(attrs={"type": "date"}),
            "details": forms.Textarea(attrs={"rows": 4}),
        }


def home(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()

            default_from = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")
            business_email = getattr(settings, "BUSINESS_EMAIL", default_from)

            subject_biz = f"[Honeybee Order] {order.name} ({order.get_choice_display()}) {order.date_needed}"
            message_biz = (
                f"New order received:\n\n"
                f"Name: {order.name}\n"
                f"Email: {order.email}\n"
                f"Phone: {order.phone}\n"
                f"Pickup/Delivery: {order.get_choice_display()}\n"
                f"Date Needed: {order.date_needed}\n\n"
                f"Details:\n{order.details}\n"
                f"Order ID: {order.id}"
            )

            subject_cust = "Honeybee Bakehouse — We got your order!"
            message_cust = (
                f"Hi {order.name},\n\n"
                f"Thanks for your order with Honeybee Bakehouse. We’ll review it and follow up soon.\n\n"
                f"Summary:\n"
                f"- Pickup/Delivery: {order.get_choice_display()}\n"
                f"- Date Needed: {order.date_needed}\n"
                f"- Details: {order.details}\n\n"
                f"If anything looks off, just reply to this email.\n\n"
                f"— Honeybee Bakehouse"
            )

            try:
                send_mail(subject_biz, message_biz, default_from, [business_email], fail_silently=False)

                if order.email:
                    send_mail(subject_cust, message_cust, default_from, [order.email], fail_silently=False)

            except BadHeaderError:
                return render(
                    request,
                    "form.html",
                    {"form": form, "error": "Email could not be sent due to an invalid header. Your order was saved."},
                    status=200,
                )
            except Exception as e:
                if settings.DEBUG:
                    print("Email send error:", repr(e))
                return redirect(reverse("order_success"))

            return redirect(reverse("order_success"))
    else:
        form = OrderForm()

    return render(request, "form.html", {"form": form})


def order_success(request):
    return render(request, "thanks.html")
