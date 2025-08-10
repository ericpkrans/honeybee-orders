from django import forms
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.shortcuts import render, redirect
from django.utils.html import strip_tags

from .models import Order


# ----- Order form -----
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["name", "email", "phone", "choice", "date_needed", "details"]
        widgets = {
            "date_needed": forms.DateInput(attrs={"type": "date"}),
            "details": forms.Textarea(attrs={"rows": 5}),
        }


# ---------- Email helpers & templates ----------
BRAND_BG = "#FFF8E1"          # warm paper
BRAND_DARK = "#0B3D2E"        # deep green
BRAND_HONEY = "#F4C430"       # honey yellow
BRAND_LINK = "#1B5E20"        # green link

def send_html_email(subject: str, text_body: str, html_body: str, to_list: list[str]):
    """
    Sends a multi-part email: plaintext + HTML.
    """
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to_list,
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=False)


# --- Order confirmations (customer) ---
CONFIRM_SUBJECT = "🐝 Your Honeybee Bakehouse Order Is Buzzing Our Way!"

CONFIRM_TEXT = """Hi {name},

Thank you kindly for your order from Honeybee Bakehouse!
We’ve got it in the kitchen queue and can’t wait to bake up something sweet just for you.

Order Details:
{order_details}

We’ll reach out if we have any questions before your pickup/delivery on {date_needed}.

💌 A quick note: Sometimes our emails wander into spam or promotions folders.
If you spot us there, please mark us as Not Spam so future updates land right in your inbox.

With love and frosting,
The Honeybee Bakehouse Crew 🐝
{from_email}
"""

CONFIRM_HTML = """\
<!doctype html>
<html>
  <body style="margin:0;padding:0;background:{bg};font-family:Segoe UI,Roboto,system-ui,-apple-system,sans-serif;color:{dark}">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{bg};padding:24px 0;">
      <tr>
        <td align="center">
          <table width="640" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:16px;overflow:hidden;border:1px solid #eee">
            <tr>
              <td style="background:{honey};padding:18px 24px;color:{dark};font-weight:700;font-size:20px">
                Honeybee Bakehouse 🐝
              </td>
            </tr>
            <tr>
              <td style="padding:24px">
                <h1 style="margin:0 0 8px 0;font-size:22px;color:{dark}">Thanks, {name}!</h1>
                <p style="margin:0 0 16px 0;line-height:1.6">
                  We’ve got your order and it’s headed to our kitchen queue.
                </p>
                <table style="width:100%;background:{bg};border-radius:12px;padding:16px;margin:0 0 16px 0">
                  <tr><td style="font-weight:600;color:{dark};padding-bottom:6px">Order Details</td></tr>
                  <tr><td style="white-space:pre-wrap;line-height:1.6;color:{dark}">{order_details}</td></tr>
                </table>
                <p style="margin:0 0 12px 0;line-height:1.6">
                  Pickup/Delivery date: <strong>{date_needed}</strong>
                </p>
                <p style="margin:0 0 16px 0;line-height:1.6">
                  💌 Sometimes our emails wander into spam/promotions. If you spot us there,
                  please mark as <em>Not Spam</em> so future updates land right in your inbox.
                </p>
                <p style="margin:0;line-height:1.6">With love and frosting,<br>— The Honeybee Bakehouse Crew 🐝</p>
              </td>
            </tr>
            <tr>
              <td style="padding:16px 24px;font-size:12px;color:#666;border-top:1px solid #eee">
                From: {from_email}
              </td>
            </tr>
          </table>
          <p style="color:#999;font-size:11px;margin:12px 0 0 0">
            You’re receiving this because you placed an order at Honeybee Bakehouse.
          </p>
        </td>
      </tr>
    </table>
  </body>
</html>
""".format(bg=BRAND_BG, dark=BRAND_DARK, honey=BRAND_HONEY, name="{name}",
           order_details="{order_details}", date_needed="{date_needed}", from_email="{from_email}")


# --- Internal notification (business inbox) ---
ADMIN_SUBJECT = "New Honeybee Order from {name} ({choice}) on {date_needed}"

ADMIN_TEXT = """A new order just came in. 🐝

Name: {name}
Email: {email}
Phone: {phone}
Pickup/Delivery: {choice}
Date needed: {date_needed}

Details:
{order_details}
"""

ADMIN_HTML = """\
<!doctype html>
<html>
  <body style="margin:0;padding:24px;background:#fafafa;font-family:Segoe UI,Roboto,system-ui,-apple-system,sans-serif;color:#222">
    <table width="640" align="center" cellpadding="0" cellspacing="0" style="background:#fff;border:1px solid #eee;border-radius:12px;overflow:hidden">
      <tr><td style="background:{honey};padding:14px 18px;font-weight:700">🐝 New Order Notification</td></tr>
      <tr>
        <td style="padding:18px;line-height:1.6">
          <p style="margin:0 0 6px 0"><strong>Name:</strong> {name}</p>
          <p style="margin:0 0 6px 0"><strong>Email:</strong> {email}</p>
          <p style="margin:0 0 6px 0"><strong>Phone:</strong> {phone}</p>
          <p style="margin:0 0 6px 0"><strong>Pickup/Delivery:</strong> {choice}</p>
          <p style="margin:0 0 12px 0"><strong>Date needed:</strong> {date_needed}</p>
          <p style="margin:0 0 6px 0"><strong>Details:</strong></p>
          <pre style="white-space:pre-wrap;margin:0">{order_details}</pre>
        </td>
      </tr>
    </table>
  </body>
</html>
""".format(honey=BRAND_HONEY, name="{name}", email="{email}", phone="{phone}",
           choice="{choice}", date_needed="{date_needed}", order_details="{order_details}")


def _choice_display(code: str) -> str:
    return {"P": "Pick-up", "D": "Delivery"}.get(code, code)


def _send_emails(order: Order):
    date_str = order.date_needed.strftime("%b %d, %Y")
    choice_str = _choice_display(order.choice)

    # Customer confirmation
    confirm_text = CONFIRM_TEXT.format(
        name=order.name,
        order_details=order.details,
        date_needed=date_str,
        from_email=settings.DEFAULT_FROM_EMAIL,
    )
    confirm_html = CONFIRM_HTML.format(
        name=order.name,
        order_details=order.details,
        date_needed=date_str,
        from_email=settings.DEFAULT_FROM_EMAIL,
    )
    send_html_email(CONFIRM_SUBJECT, confirm_text, confirm_html, [order.email])

    # Business notification
    admin_text = ADMIN_TEXT.format(
        name=order.name,
        email=order.email,
        phone=order.phone,
        choice=choice_str,
        date_needed=date_str,
        order_details=order.details,
    )
    admin_html = ADMIN_HTML.format(
        name=order.name,
        email=order.email,
        phone=order.phone,
        choice=choice_str,
        date_needed=date_str,
        order_details=order.details,
    )
    send_html_email(
        ADMIN_SUBJECT.format(name=order.name, choice=choice_str, date_needed=date_str),
        admin_text,
        admin_html,
        [settings.BUSINESS_EMAIL],
    )


# ---------- Views ----------
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


def landing(request):
    return render(request, "landing.html")

# --- Landing + Rewards pages ---

def landing_page(request):
    # Simple render; assets and audio handled in the template
    return render(request, "landing.html")

def rewards(request):
    if request.method == "POST":
        # Optional: capture email and notify business inbox
        email = request.POST.get("email", "").strip()
        name = request.POST.get("name", "").strip()
        if email:
            subject = "New Southern Sweets Club signup"
            body = f"Name: {name or '(not provided)'}\nEmail: {email}\n"
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.BUSINESS_EMAIL],
                fail_silently=False,
            )
        return redirect("rewards_thanks")
    return render(request, "rewards.html")

def rewards_thanks(request):
    return render(request, "rewards_thanks.html")


def rewards(request):
    if request.method == "POST":
        name = strip_tags(request.POST.get("name", "")).strip()
        email = strip_tags(request.POST.get("email", "")).strip()

        if name and email:
            # Pretty welcome email to the customer
            subject = "Welcome to the Southern Sweets Club 🍪🐝"
            text_body = (
                f"Hi {name},\n\n"
                "You're in! Thanks for joining the Southern Sweets Club.\n"
                "Show this email at pickup/delivery to claim your 6 FREE snickerdoodles.\n\n"
                "We’ll send weekly flavors & specials.\n\n— Honeybee Bakehouse"
            )
            html_body = f"""\
            <!doctype html>
            <html>
              <body style="margin:0;padding:0;background:{BRAND_BG};font-family:Segoe UI,Roboto,system-ui,-apple-system,sans-serif;color:{BRAND_DARK}">
                <table width="100%" cellpadding="0" cellspacing="0" style="padding:24px 0;background:{BRAND_BG}">
                  <tr><td align="center">
                    <table width="640" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:16px;overflow:hidden;border:1px solid #eee">
                      <tr><td style="background:{BRAND_HONEY};padding:18px 24px;font-weight:700">Southern Sweets Club</td></tr>
                      <tr><td style="padding:24px;line-height:1.6">
                        <h1 style="margin:0 0 10px 0">Welcome, {name}! 🍪🐝</h1>
                        <p style="margin:0 0 12px 0">You're in! Thanks for joining the Southern Sweets Club.</p>
                        <p style="margin:0 0 12px 0"><strong>Perk:</strong> Show this email at pickup/delivery to claim your <strong>6 FREE snickerdoodles</strong>.</p>
                        <p style="margin:0">We’ll send weekly flavors & specials. See you soon!</p>
                        <p style="margin:12px 0 0 0">— Honeybee Bakehouse</p>
                      </td></tr>
                    </table>
                  </td></tr>
                </table>
              </body>
            </html>
            """
            send_html_email(subject, text_body, html_body, [email])

            # Notify business
            send_mail(
                "New Southern Sweets Club signup",
                f"Name: {name}\nEmail: {email}\n",
                settings.DEFAULT_FROM_EMAIL,
                [settings.BUSINESS_EMAIL],
                fail_silently=False,
            )
            return redirect("rewards_thanks")

    return render(request, "rewards.html")


def rewards_thanks(request):
    return render(request, "rewards_thanks.html")
