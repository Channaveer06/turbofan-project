import json
import numpy as np
import pandas as pd
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse
from django.contrib.auth import authenticate, login

from .model_utils import (
    predict_rul, get_engine_status, get_life_percent, FEATURE_COLS
)


# 🔹 LANDING PAGE
def landing(request):
    return render(request, 'landing.html')




# 🔹 LOGIN (REAL DJANGO AUTH)
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)   # 🔥 creates session
            return redirect('upload')

        return render(request, 'login.html', {
            'error': 'Invalid username or password'
        })

    return render(request, 'login.html')

from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('login')
# 🔹 UPLOAD VIEW
def upload_view(request):
    context = {'feature_cols_list': FEATURE_COLS}

    if request.method == 'POST':

        # ================= DEMO MODE =================
        if request.POST.get('demo') == '1':
            try:
                # 🔥 Generate realistic random data
                sample = np.random.rand(40, len(FEATURE_COLS))
                df = pd.DataFrame(sample, columns=FEATURE_COLS)

                rul, err = predict_rul(df)
                if err:
                    context['error'] = err
                    return render(request, 'upload.html', context)

                status, status_class, recommendation = get_engine_status(rul)
                life_pct = get_life_percent(rul)

                # 🔥 LAST ROW (LATEST ENGINE STATE)
                last_row = df.iloc[-1].to_dict()

                # 🔥 DEBUG (optional)
                print("DEMO SENSOR DATA:", last_row)

                request.session['result'] = {
                    'rul': int(rul),
                    'status': status,
                    'status_class': status_class,
                    'recommendation': recommendation,
                    'life_pct': life_pct,
                    'cycles_used': 100 - life_pct,
                    'sensor_data': last_row,   # ✅ REAL DATA
                    'is_demo': True,
                }

                return redirect('dashboard')

            except Exception as e:
                context['error'] = f"Demo error: {str(e)}"
                return render(request, 'upload.html', context)


        # ================= FILE UPLOAD =================
        if 'file' in request.FILES:
            file = request.FILES['file']

            try:
                df = pd.read_csv(file)
            except Exception as e:
                context['error'] = f"Could not read CSV: {str(e)}"
                return render(request, 'upload.html', context)

            # 🔥 Check required columns
            missing = [col for col in FEATURE_COLS if col not in df.columns]
            if missing:
                context['error'] = f"Missing columns: {', '.join(missing)}"
                return render(request, 'upload.html', context)

            try:
                rul, err = predict_rul(df)
                if err:
                    context['error'] = err
                    return render(request, 'upload.html', context)

                status, status_class, recommendation = get_engine_status(rul)
                life_pct = get_life_percent(rul)

                # 🔥 LAST ROW = CURRENT ENGINE STATE
                last_row = df.iloc[-1].to_dict()

                # 🔥 DEBUG (VERY IMPORTANT)
                print("REAL SENSOR DATA:", last_row)

                request.session['result'] = {
                    'rul': int(rul),
                    'status': status,
                    'status_class': status_class,
                    'recommendation': recommendation,
                    'life_pct': life_pct,
                    'cycles_used': 100 - life_pct,
                    'sensor_data': last_row,   # ✅ REAL DATA
                    'is_demo': False,
                }

                return redirect('dashboard')

            except Exception as e:
                context['error'] = f"Processing error: {str(e)}"
                return render(request, 'upload.html', context)

        context['error'] = 'Please select a CSV file.'

    return render(request, 'upload.html', context)


# 🔹 DASHBOARD
def dashboard_view(request):
    result = request.session.get('result')

    if not result:
        return redirect('upload')

    # 🔥 DEBUG CHECK
    print("SESSION DATA:", result)

    return render(request, 'dashboard.html', result)


# 🔹 HOME
def home(request):
    return redirect('landing')


# 🔹 API
@csrf_exempt
def api_predict(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    try:
        df = pd.read_csv(request.FILES['file'])
    except Exception as e:
        return JsonResponse({'error': f'Could not read CSV: {str(e)}'}, status=400)

    missing = [col for col in FEATURE_COLS if col not in df.columns]
    if missing:
        return JsonResponse({'error': f'Missing columns: {missing}'}, status=400)

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
    from django.http import HttpResponse

def download_report(request):
    result = request.session.get('result')

    if not result:
        return HttpResponse("No data available")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="engine_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []

    # Title
    content.append(Paragraph("<b>AERO_CORE ENGINE REPORT</b>", styles['Title']))
    content.append(Spacer(1, 20))

    # Data
    content.append(Paragraph(f"<b>Status:</b> {result.get('status')}", styles['Normal']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"<b>Remaining Useful Life (RUL):</b> {result.get('rul')} cycles", styles['Normal']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"<b>Life Percentage:</b> {result.get('life_pct')}%", styles['Normal']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"<b>Cycles Used:</b> {result.get('cycles_used')}%", styles['Normal']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"<b>Recommendation:</b> {result.get('recommendation')}", styles['Normal']))
    content.append(Spacer(1, 20))

    content.append(Paragraph("Generated by AERO_CORE AI System", styles['Italic']))

    doc.build(content)

    return response