# orderform/views.py
from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .models import Order

# --- ModelForm for the order ---
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["name", "email", "phone", "choice", "date_needed", "details"]
        widgets = {
            "date_needed": forms.DateInput(attrs={"type": "date"}),
            "details": forms.Textarea(attrs={"rows": 5}),
        }

# --- Friendly Honeybee confirmation template ---
CONFIRM_SUBJECT = "🐝 Your Honeybee Bakehouse Order Is Buzzing Our Way!"

CONFIRM_BODY = """Hi {name},

Thank you kindly for your order from Honeybee Bakehouse!
We’ve got it in the kitchen queue and can’t wait to bake up something sweet just for you.

Order Details:
{order_details}

We’ll reach out if we have any questions before your pickup/delivery on {date_needed}.

💌 A quick note: Sometimes our emails wander into spam or promotions folders (bless their hearts).
If you spot us there, please mark us as Not Spam so future updates land right in your inbox.

Thanks for supporting our small, Southern kitchen — we’re so glad you’re part of the Honeybee family!

With love and frosting,
The Honeybee Bakehouse Crew 🐝
{from_email}
"""

# --- Internal notification to business inbox ---
ADMIN_SUBJECT = "New Honeybee Order from {name} ({choice}) on {date_needed}"
ADMIN_BODY = """A new order just came in. 🐝

Name: {name}
Email: {email}
Phone: {phone}
Pickup/Delivery: {choice}
Date needed: {date_needed}

Details:
{order_details}
"""

def _choice_display(code: str) -> str:
    # Map model choices to human text
    return {"P": "Pick-up", "D": "Delivery"}.get(code, code)

def _send_emails(order: Order):
    # Format values
    date_str = order.date_needed.strftime("%b %d, %Y")
    choice_str = _choice_display(order.choice)

    # Customer confirmation
    confirm_msg = CONFIRM_BODY.format(
        name=order.name,
        order_details=order.details,
        date_needed=date_str,
        from_email=settings.DEFAULT_FROM_EMAIL,
    )
    send_mail(
        subject=CONFIRM_SUBJECT,
        message=confirm_msg,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        fail_silently=False,
    )

    # Business notification
    admin_msg = ADMIN_BODY.format(
        name=order.name,
        email=order.email,
        phone=order.phone,
        choice=choice_str,
        date_needed=date_str,
        order_details=order.details,
    )
    send_mail(
        subject=ADMIN_SUBJECT.format(name=order.name, choice=choice_str, date_needed=date_str),
        message=admin_msg,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.BUSINESS_EMAIL],
        fail_silently=False,
    )

# --- Views ---
def home(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            _send_emails(order)
            return redirect("thanks")
    else:
        form = OrderForm()
    return render(request, "form.html", {"form": form})

def thanks(request):
    return render(request, "thanks.html")
