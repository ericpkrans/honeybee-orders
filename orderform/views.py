from django.conf import settings
from django.shortcuts import render, redirect
from django.views import View
from django.core.mail import send_mail
from .forms import OrderForm

class OrderCreate(View):
    def get(self, request):
        return render(request, "orders/form.html", {"form": OrderForm()})

    def post(self, request):
        form = OrderForm(request.POST)
        if not form.is_valid():
            return render(request, "orders/form.html", {"form": form})

        order = form.save()

        subject = f"New Honeybee Order #{order.id}"
        body = (
            f"Name: {order.name}\n"
            f"Email: {order.email}\n"
            f"Phone: {order.phone}\n"
            f"Choice: {'Pick-up' if order.choice=='P' else 'Delivery'}\n"
            f"Date needed: {order.date_needed}\n"
            f"Details:\n{order.details}\n"
        )

        # To business
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [settings.BUSINESS_EMAIL],
            fail_silently=True,
        )

        # Confirmation to customer
        send_mail(
            "We got your Honeybee Bakehouse order!",
            "Thanks! We’ll confirm details soon.\n\n" + body,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            fail_silently=True,
        )

        return redirect("thanks")

def thanks(request):
    return render(request, "orders/thanks.html")
