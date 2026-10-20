from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginFormAuthentication
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.db.models import F
from django.conf import settings
from django.utils import timezone
from django.views.decorators.http import require_POST
from axes.helpers import get_client_ip_address
from .models import RequestThrottleBucket
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json
import urllib.parse
import sweetify
import hashlib
from datetime import datetime, timezone as datetime_timezone

MAX_RECAPTCHA_TOKEN_LENGTH = 8192

# Create your views here.

def index(request):
    login_form = LoginFormAuthentication(request, data=request.POST)
    register_form = RegistrationForm(request.POST)
    context = {
        'login_form': login_form,
        'register_form': register_form,
        'recaptcha_site_key': settings.GOOGLE_RECAPTCHA_SITE_KEY,
    }
    
    return render(request, "home/index.html", context)

def _verify_recaptcha(response_token):
    secret_key = settings.GOOGLE_RECAPTCHA_SECRET_KEY
    if not secret_key or not response_token:
        return False

    payload = urllib.parse.urlencode({
        'secret': secret_key,
        'response': response_token,
    }).encode()
    verification_request = Request(
        'https://www.google.com/recaptcha/api/siteverify',
        data=payload,
    )
    try:
        with urlopen(verification_request, timeout=5) as response:
            result = json.loads(response.read().decode('utf-8'))
    except (HTTPError, URLError, TimeoutError, ValueError, UnicodeError):
        return False

    return isinstance(result, dict) and result.get('success') is True


def _allow_limited_request(request, scope, limit, window_seconds):
    client_ip = get_client_ip_address(request) or request.META.get('REMOTE_ADDR')
    if not client_ip:
        return False

    now = timezone.now()
    window_start = int(now.timestamp() // window_seconds) * window_seconds
    bucket_key = hashlib.sha256(
        f'{scope}:{client_ip}:{window_start}'.encode('utf-8'),
    ).hexdigest()
    expires_at = datetime.fromtimestamp(
        window_start + window_seconds,
        tz=datetime_timezone.utc,
    )

    with transaction.atomic():
        RequestThrottleBucket.objects.filter(expires_at__lte=now).delete()
        try:
            with transaction.atomic():
                RequestThrottleBucket.objects.create(
                    bucket_key=bucket_key,
                    count=1,
                    expires_at=expires_at,
                )
            return True
        except IntegrityError:
            updated = RequestThrottleBucket.objects.filter(
                bucket_key=bucket_key,
                count__lt=limit,
            ).update(count=F('count') + 1)
            return updated == 1


@require_POST
def loginForm(request):
    response_token = request.POST.get('g-recaptcha-response')
    if not response_token or len(response_token) > MAX_RECAPTCHA_TOKEN_LENGTH or not response_token.isascii():
        sweetify.toast(request, 'Invalid reCAPTCHA. Please try again.', icon="error", timer=1000)
        return redirect("Home")
    if not _allow_limited_request(request, 'recaptcha-siteverify', limit=60, window_seconds=60):
        sweetify.toast(request, 'Too many attempts. Please wait and try again.', icon="error", timer=2000)
        return redirect("Home")

    if not _verify_recaptcha(response_token):
        sweetify.toast(request, 'Invalid reCAPTCHA. Please try again.', icon="error", timer=1000)
        return redirect("Home")

    form = LoginFormAuthentication(request, data=request.POST)
    if form.is_valid():
        login(request, form.get_user())
        sweetify.toast(request, 'Succesfully logged in!', icon="success", timer=1000)
    else:
        sweetify.toast(request, 'Invalid Username or Password!', icon="error", timer=2000)
    return redirect("Home")

@require_POST
def registerForm(request):
    response_token = request.POST.get('g-recaptcha-response')
    if not response_token or len(response_token) > MAX_RECAPTCHA_TOKEN_LENGTH or not response_token.isascii():
        sweetify.toast(request, 'Invalid reCAPTCHA. Please try again.', icon="error", timer=1000)
        return redirect("Home")
    if not _allow_limited_request(request, 'recaptcha-siteverify', limit=60, window_seconds=60):
        sweetify.toast(request, 'Too many attempts. Please wait and try again.', icon="error", timer=2000)
        return redirect("Home")
    if not _verify_recaptcha(response_token):
        sweetify.toast(request, 'Invalid reCAPTCHA. Please try again.', icon="error", timer=1000)
        return redirect("Home")

    form = RegistrationForm(request.POST)
    if form.is_valid():
        if not _allow_limited_request(request, 'account-creation', limit=5, window_seconds=3600):
            sweetify.toast(request, 'Too many accounts created. Please try again later.', icon="error", timer=2000)
            return redirect("Home")
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        sweetify.toast(request, 'Account created. Staff must approve access before you can sign in.', icon="success", timer=3500)
    else:
        sweetify.toast(request, 'Registration details are invalid. Please try again.', icon="error", timer=2000)
    return redirect("Home")

@require_POST
def logout_request(request):
    logout(request)
    sweetify.toast(request, 'Succesfully logged out!', icon="success", timer=2500)
    return redirect("/")

def admin_panel(request):
    return redirect("admin/")
