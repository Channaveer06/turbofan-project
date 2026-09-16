import json
import numpy as np
import pandas as pd
import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

from .models import SignupRequest
from .model_utils import (
    predict_rul, get_engine_status, get_life_percent, FEATURE_COLS
)

# 🔥 GLOBAL LOG STORAGE
logs = []


# 🔹 LANDING
def landing(request):
    return render(request, 'landing.html')


# 🔹 LOGIN
def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )

        if user:
            login(request, user)
            return redirect('upload')

        return render(request, 'login.html', {'error': 'Invalid username or password'})

    return render(request, 'login.html')


# 🔹 LOGOUT
def logout_view(request):
    logout(request)
    return redirect('login')


# 🔹 UPLOAD
def upload_view(request):
    context = {'feature_cols_list': FEATURE_COLS}

    if request.method == 'POST':

        # DEMO MODE
        if request.POST.get('demo') == '1':
            try:
                df = pd.DataFrame(
                    np.random.rand(40, len(FEATURE_COLS)),
                    columns=FEATURE_COLS
                )

                rul, err = predict_rul(df)
                if err:
                    context['error'] = err
                    return render(request, 'upload.html', context)

                status, status_class, recommendation = get_engine_status(rul)
                life_pct = get_life_percent(rul)

                result_data = {
                    'rul': int(rul),
                    'status': status,
                    'status_class': status_class,
                    'recommendation': recommendation,
                    'life_pct': life_pct,
                    'cycles_used': 100 - life_pct,
                    'sensor_data': df.iloc[-1].to_dict(),
                    'is_demo': True,
                }

                logs.append({
                    "engine_id": "DEMO",
                    "rul": int(rul),
                    "status": status,
                    "time": datetime.datetime.now().strftime("%H:%M"),
                    "date": datetime.datetime.now().strftime("%d %b"),
                    "result": result_data
                })

                request.session['result'] = result_data
                return redirect('dashboard')

            except Exception as e:
                context['error'] = str(e)

        # FILE UPLOAD
        if 'file' in request.FILES:
            try:
                df = pd.read_csv(request.FILES['file'])
            except Exception as e:
                context['error'] = str(e)
                return render(request, 'upload.html', context)

            missing = [c for c in FEATURE_COLS if c not in df.columns]
            if missing:
                context['error'] = f"Missing columns: {', '.join(missing)}"
                return render(request, 'upload.html', context)

            rul, err = predict_rul(df)
            if err:
                context['error'] = err
                return render(request, 'upload.html', context)

            status, status_class, recommendation = get_engine_status(rul)
            life_pct = get_life_percent(rul)

            result_data = {
                'rul': int(rul),
                'status': status,
                'status_class': status_class,
                'recommendation': recommendation,
                'life_pct': life_pct,
                'cycles_used': 100 - life_pct,
                'sensor_data': df.iloc[-1].to_dict(),
                'is_demo': False,
            }

            logs.append({
                "engine_id": "REAL",
                "rul": int(rul),
                "status": status,
                "time": datetime.datetime.now().strftime("%H:%M"),
                "date": datetime.datetime.now().strftime("%d %b"),
                "result": result_data
            })

            request.session['result'] = result_data
            return redirect('dashboard')

        context['error'] = 'Please select a CSV file.'

    return render(request, 'upload.html', context)


# 🔹 DASHBOARD
def dashboard_view(request):
    result = request.session.get('result')
    if not result:
        return redirect('upload')
    return render(request, 'dashboard.html', result)


# 🔹 LOGS
def logs_view(request):
    return render(request, 'logs.html', {"logs": logs})


def view_log(request, index):
    try:
        request.session['result'] = logs[index]['result']
        return redirect('dashboard')
    except:
        return redirect('logs')


# 🔹 API
@csrf_exempt
def api_predict(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file'}, status=400)

    df = pd.read_csv(request.FILES['file'])

    rul, err = predict_rul(df)
    if err:
        return JsonResponse({'error': err}, status=400)

    status, _, recommendation = get_engine_status(rul)

    return JsonResponse({
        'rul': round(rul, 2),
        'status': status,
        'recommendation': recommendation,
        'life_percent': get_life_percent(rul),
    })


# 🔹 DOWNLOAD REPORT
def download_report(request):
    result = request.session.get('result')
    if not result:
        return HttpResponse("No data")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()

    content = [
        Paragraph("<b>AERO_CORE REPORT</b>", styles['Title']),
        Spacer(1, 20),
        Paragraph(f"Status: {result['status']}", styles['Normal']),
        Paragraph(f"RUL: {result['rul']}", styles['Normal']),
        Paragraph(f"Life: {result['life_pct']}%", styles['Normal']),
    ]

    doc.build(content)
    return response


# 🔹 SIGNUP
def signup_request(request):
    if request.method == "POST":
        SignupRequest.objects.create(
            username=request.POST['username'],
            email=request.POST['email'],
            password=request.POST['password']
        )
        return render(request, "request_sent.html")

    return render(request, "signup.html")


# 🔹 APPROVE
def approve_user(request, id):
    req = get_object_or_404(SignupRequest, id=id)

    if User.objects.filter(username=req.username).exists():
        req.delete()
        return HttpResponse("User already exists")

    User.objects.create_user(
        username=req.username,
        email=req.email,
        password=req.password
    )

    send_mail(
        "AERO_CORE Approved",
        f"Hello {req.username}, your account is approved.\nLogin: http://127.0.0.1:8000/login/",
        "channaveer06@gmail.com",
        [req.email],
    )

    req.delete()

    return render(request, "approve_success.html", {
        "username": req.username,
        "email": req.email
    })


# 🔹 REJECT
def reject_user(request, id):
    req = get_object_or_404(SignupRequest, id=id)
    req.delete()
    return redirect('admin_panel')


# 🔹 DELETE USER
def delete_user(request, id):
    user = get_object_or_404(User, id=id)

    if user.is_superuser:
        return HttpResponse("Cannot delete admin")

    user.delete()
    return redirect('admin_panel')


# 🔒 ADMIN PANEL
def is_admin(user):
    return user.is_superuser


@user_passes_test(is_admin)
def admin_panel(request):
    return render(request, "admin_panel.html", {
        # 🔥 ONLY PENDING REQUESTS
        "requests": SignupRequest.objects.filter(is_approved=False),

        # 🔥 ALL USERS
        "users": User.objects.all()
    })