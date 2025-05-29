import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def register_view(request):
    if request.method == 'POST':
        data = {
            'username': request.POST.get('username'),
            'password': request.POST.get('password'),
            'email': request.POST.get('email'),
        }
        api_url = 'http://127.0.0.1:8000/diary/api/register/'

        try:
            response = requests.post(api_url, json=data)
            if response.status_code == 201:
                messages.success(request, 'Kullanıcı başarıyla oluşturuldu.')
                return redirect('login-view')
            else:
                messages.error(request, 'Kayıt başarısız: ' + str(response.json()))
        except requests.exceptions.RequestException:
            messages.error(request, 'API sunucusuna ulaşılamadı.')

    return render(request, 'registration/register.html')



def login_view(request):
    if request.method == 'POST':
        data = {
            'username': request.POST.get('username'),
            'password': request.POST.get('password'),
        }

        api_url = 'http://127.0.0.1:8000/diary/api/login/'  # API endpoint

        try:
            response = requests.post(api_url, json=data)

            if response.status_code == 200:
                tokens = response.json()
                access_token = tokens.get('access')
                refresh_token = tokens.get('refresh')

                username = data['username']
                request.session['username'] = username


                request.session['access_token'] = access_token
                request.session['refresh_token'] = refresh_token

                messages.success(request, 'Giriş başarılı!')
                return redirect('frontenddiaryapp:anasayfa')  # Bu view url name olarak tanımlanmalı

            else:
                error = response.json().get('non_field_errors', ['Bilinmeyen hata'])[0]
                messages.error(request, f'Giriş başarısız: {error}')
                return render(request, 'frontenddiaryapp/login.html')

        except requests.exceptions.RequestException:
            messages.error(request, 'Sunucuya ulaşılamadı.')
            return render(request, 'frontenddiaryapp/login.html')

    return render(request, 'registration/login.html')



def home_view(request):
    if not request.session.get('access_token'):
        messages.error(request, "Lütfen giriş yapın.")
        return redirect('login-view')
    
    username = request.session.get('username', '')  # username session'da varsa al, yoksa boş string
    context = {
        'username': username,
    }
    return render(request, 'frontenddiaryapp/index.html', context)




def logout_view(request):
    if 'access_token' in request.session:
        del request.session['access_token']
    if 'refresh_token' in request.session:
        del request.session['refresh_token']
    request.session.flush()  # sessiondaki diğer tüm verileri de temizler

    messages.success(request, "Başarıyla çıkış yaptınız.")
    return redirect('login-view')  # login sayfasına yönlendir



def add_diary_view(request):
    if not request.session.get('access_token'):
        messages.error(request, 'Giriş yapmalısınız.')
        return redirect('login-view')

    if request.method == 'POST':
        access_token = request.session.get('access_token')
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        data = {
            'title': request.POST.get('title'),
            'content': request.POST.get('content'),
            'date': request.POST.get('date')
        }

        api_url = 'http://127.0.0.1:8000/diary/api/diaries/'  # kendi API endpoint’in

        try:
            response = requests.post(api_url, headers=headers, json=data, timeout=5)

            if response.status_code == 201:
                messages.success(request, 'Günlük başarıyla eklendi.')
                
            else:
                messages.error(request, f'API Hatası: {response.status_code} - {response.json()}')

        except requests.exceptions.RequestException as e:
            messages.error(request, f'Bağlantı hatası: {str(e)}')

    return render(request, 'frontenddiaryapp/adddiary.html')


def diary_list_view(request):
    if not request.session.get('access_token'):
        messages.error(request, 'Giriş yapmalısınız.')
        return redirect('login-view')

    access_token = request.session.get('access_token')
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    api_url = 'http://127.0.0.1:8000/diary/api/diaries/'  # API endpoint

    try:
        response = requests.get(api_url, headers=headers, timeout=5)
        if response.status_code == 200:
            diaries = response.json()
        else:
            messages.error(request, f'API Hatası: {response.status_code}')
            diaries = []
    except requests.exceptions.RequestException as e:
        messages.error(request, f'Bağlantı hatası: {str(e)}')
        diaries = []

    return render(request, 'frontenddiaryapp/diarylist.html', {'diaries': diaries})



def diary_detail_view(request, id):
    if not request.session.get('access_token'):
        messages.error(request, 'Giriş yapmalısınız.')
        return redirect('login-view')

    access_token = request.session.get('access_token')
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    api_url = f'http://127.0.0.1:8000/diary/api/diaries/{id}/'  # API endpoint

    try:
        response = requests.get(api_url, headers=headers, timeout=5)
        if response.status_code == 200:
            diary = response.json()
            return render(request, 'frontenddiaryapp/updatediary.html', {'diary': diary})
        elif response.status_code == 404:
            messages.error(request, 'Günlük bulunamadı.')
        else:
            messages.error(request, f'API Hatası: {response.status_code}')
    except requests.exceptions.RequestException as e:
        messages.error(request, f'Bağlantı hatası: {str(e)}')

    return redirect('frontenddiaryapp:diary-list-view')  # ya da uygun başka bir sayfa


def diary_update_view(request, pk):
    if not request.session.get('access_token'):
        messages.error(request, 'Giriş yapmalısınız.')
        return redirect('login-view')

    access_token = request.session.get('access_token')
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    api_url = f'http://127.0.0.1:8000/diary/api/diaries/{pk}/'

    if request.method == 'POST':
        data = {
            'title': request.POST.get('title'),
            'content': request.POST.get('content'),
            'date': request.POST.get('date'),
        }
        try:
            response = requests.put(api_url, json=data, headers=headers, timeout=5)
            if response.status_code == 200:
                messages.success(request, 'Günlük başarıyla düzenlendi.')
                return redirect('frontenddiaryapp:diary-list-view')
            else:
                messages.error(request, f'Güncelleme hatası: {response.status_code}')
        except requests.exceptions.RequestException as e:
            messages.error(request, f'Bağlantı hatası: {str(e)}')

        # PUT başarısızsa, kullanıcıdan gelen verilerle formu tekrar doldur
        diary = {
            'title': request.POST.get('title', ''),
            'content': request.POST.get('content', ''),
            'date': request.POST.get('date', '')
        }
        return render(request, 'frontenddiaryapp/updatediary.html', {'diary': diary})

    else:
        # GET geldiğinde bu view hiçbir işlem yapmasın, ya hata ya redirect
        messages.error(request, 'Geçersiz istek.')
        return redirect('frontenddiaryapp:diary-list-view')