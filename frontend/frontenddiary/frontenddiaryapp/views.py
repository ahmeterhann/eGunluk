import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import urllib.parse
import logging


logger = logging.getLogger(__name__)

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
                logger.info(f"Yeni kullanıcı kaydı başarılı: {data['username']}")
                return redirect('login-view')
            else:
                messages.error(request, 'Kayıt başarısız: ' + str(response.json()))
                logger.warning(f"Kayıt başarısız: {response.json()}")
        except requests.exceptions.RequestException as e:
            messages.error(request, 'API sunucusuna ulaşılamadı.')
            logger.error(f"API isteği sırasında hata: {str(e)}")

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
                logger.info(f"Kullanıcı giriş yaptı: {username}")
                return redirect('frontenddiaryapp:anasayfa')

            else:
                error = response.json().get('non_field_errors', ['Bilinmeyen hata'])[0]
                messages.error(request, f'Giriş başarısız: {error}')
                logger.warning(f"Giriş başarısız: {error} — Kullanıcı: {data['username']}")
                return render(request, 'frontenddiaryapp/login.html')

        except requests.exceptions.RequestException as e:
            messages.error(request, 'Sunucuya ulaşılamadı.')
            logger.error(f"API isteği sırasında hata: {str(e)}")
            return render(request, 'frontenddiaryapp/login.html')

    return render(request, 'registration/login.html')



def home_view(request):
    if not request.session.get('access_token'):
        logger.warning("Giriş yapılmadan anasayfa erişimi denendi.")
        messages.error(request, "Lütfen giriş yapın.")
        return redirect('login-view')
    
    username = request.session.get('username', '')
    logger.info(f"Anasayfa görüntülendi. Kullanıcı: {username}")
    context = {
        'username': username,
    }
    return render(request, 'frontenddiaryapp/index.html', context)




def logout_view(request):
    username = request.session.get('username', 'Bilinmeyen kullanıcı')
    logger.info(f"Kullanıcı çıkış yaptı: {username}")

    if 'access_token' in request.session:
        del request.session['access_token']
    if 'refresh_token' in request.session:
        del request.session['refresh_token']
    request.session.flush()  # sessiondaki diğer tüm verileri de temizler

    messages.success(request, "Başarıyla çıkış yaptınız.")
    return redirect('login-view')



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

        api_url = 'http://127.0.0.1:8000/diary/api/diaries/'

        try:
            response = requests.post(api_url, headers=headers, json=data, timeout=5)

            if response.status_code == 201:
                logger.info(f"Günlük başarıyla eklendi. Kullanıcı: {request.session.get('username')}, Başlık: {data['title']}")
                messages.success(request, 'Günlük başarıyla eklendi.')
            else:
                logger.warning(f"API Hatası: {response.status_code} - {response.json()} Kullanıcı: {request.session.get('username')}")
                messages.error(request, f'API Hatası: {response.status_code} - {response.json()}')

        except requests.exceptions.RequestException as e:
            logger.error(f"Bağlantı hatası: {str(e)} Kullanıcı: {request.session.get('username')}")
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
    api_url = 'http://127.0.0.1:8000/diary/api/diaries/'

    try:
        response = requests.get(api_url, headers=headers, timeout=5)
        if response.status_code == 200:
            diaries = response.json()
            logger.info(f"Günlükler başarıyla listelendi. Kullanıcı: {request.session.get('username')}")
        else:
            logger.warning(f"API hatası: {response.status_code} Kullanıcı: {request.session.get('username')}")
            messages.error(request, f'API Hatası: {response.status_code}')
            diaries = []
    except requests.exceptions.RequestException as e:
        logger.error(f"Bağlantı hatası: {str(e)} Kullanıcı: {request.session.get('username')}")
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
    api_url = f'http://127.0.0.1:8000/diary/api/diaries/{id}/'

    try:
        response = requests.get(api_url, headers=headers, timeout=5)
        if response.status_code == 200:
            diary = response.json()
            logger.info(f"Günlük detay görüntülendi. Kullanıcı: {request.session.get('username')}, Günlük ID: {id}")
            return render(request, 'frontenddiaryapp/updatediary.html', {'diary': diary})
        elif response.status_code == 404:
            messages.error(request, 'Günlük bulunamadı.')
            logger.warning(f"Günlük bulunamadı. Kullanıcı: {request.session.get('username')}, Günlük ID: {id}")
        else:
            messages.error(request, f'API Hatası: {response.status_code}')
            logger.warning(f"API hatası. Kullanıcı: {request.session.get('username')}, Günlük ID: {id}, Durum Kodu: {response.status_code}")
    except requests.exceptions.RequestException as e:
        messages.error(request, f'Bağlantı hatası: {str(e)}')
        logger.error(f"Bağlantı hatası: {str(e)} Kullanıcı: {request.session.get('username')}, Günlük ID: {id}")

    return redirect('frontenddiaryapp:diary-list-view')




def diary_update_view(request, pk):
    if not request.session.get('access_token'):
        logger.warning('Yetkisiz erişim denemesi - güncelleme sayfası, kullanıcı giriş yapmamış.')
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
                logger.info(f'Günlük başarıyla güncellendi. ID: {pk}, Kullanıcı: {request.session.get("username")}')
                messages.success(request, 'Günlük başarıyla düzenlendi.')
                return redirect('frontenddiaryapp:diary-list-view')
            else:
                logger.error(f'Günlük güncelleme hatası. ID: {pk}, Durum Kodu: {response.status_code}')
                messages.error(request, f'Güncelleme hatası: {response.status_code}')
        except requests.exceptions.RequestException as e:
            logger.error(f'Günlük güncelleme bağlantı hatası: {str(e)}')
            messages.error(request, f'Bağlantı hatası: {str(e)}')

        diary = {
            'title': request.POST.get('title', ''),
            'content': request.POST.get('content', ''),
            'date': request.POST.get('date', '')
        }
        return render(request, 'frontenddiaryapp/updatediary.html', {'diary': diary})

    else:
        try:
            response = requests.get(api_url, headers=headers, timeout=5)
            if response.status_code == 200:
                diary = response.json()
                logger.info(f'Günlük düzenleme sayfası açıldı. ID: {pk}, Kullanıcı: {request.session.get("username")}')
                return render(request, 'frontenddiaryapp/updatediary.html', {'diary': diary})
            elif response.status_code == 404:
                logger.warning(f'Günlük bulunamadı. ID: {pk}, Kullanıcı: {request.session.get("username")}')
                messages.error(request, 'Günlük bulunamadı.')
            else:
                logger.error(f'API hatası. ID: {pk}, Durum Kodu: {response.status_code}')
                messages.error(request, f'API Hatası: {response.status_code}')
        except requests.exceptions.RequestException as e:
            logger.error(f'Günlük veri çekme bağlantı hatası: {str(e)}')
            messages.error(request, f'Bağlantı hatası: {str(e)}')

        return redirect('frontenddiaryapp:diary-list-view')

    

def diary_delete_view(request, pk):
    if not request.session.get('access_token'):
        logger.warning('Yetkisiz erişim denemesi - günlük silme, kullanıcı giriş yapmamış.')
        messages.error(request, 'Giriş yapmalısınız.')
        return redirect('login-view')

    access_token = request.session.get('access_token')
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    api_url = f'http://127.0.0.1:8000/diary/api/diaries/{pk}/'

    try:
        response = requests.delete(api_url, headers=headers, timeout=5)
        if response.status_code == 204:
            logger.info(f'Günlük başarıyla silindi. ID: {pk}, Kullanıcı: {request.session.get("username")}')
            messages.success(request, 'Günlük başarıyla silindi.')
        else:
            logger.error(f'Günlük silme hatası. ID: {pk}, Durum Kodu: {response.status_code}')
            messages.error(request, f'Silme hatası: {response.status_code}')
    except requests.exceptions.RequestException as e:
        logger.error(f'Günlük silme bağlantı hatası: {str(e)}')
        messages.error(request, f'Bağlantı hatası: {str(e)}')

    return redirect('frontenddiaryapp:diary-list-view')





def search_results_view(request):
    query = request.GET.get('q', '')
    diaries = []
    if query:
        access_token = request.session.get('access_token')
        if not access_token:
            logger.warning('Yetkisiz arama denemesi - kullanıcı giriş yapmamış.')
            messages.error(request, 'Önce giriş yapmalısınız.')
            return redirect('login-view')

        headers = {'Authorization': f'Bearer {access_token}'}
        encoded_query = urllib.parse.quote(query)
        api_url = f"http://127.0.0.1:8000/diary/api/diaries/search/?q={encoded_query}"

        try:
            logger.info(f"Arama yapılıyor. Kullanıcı: {request.session.get('username')}, Sorgu: '{query}'")
            response = requests.get(api_url, headers=headers, timeout=5)
            if response.status_code == 200:
                diaries = response.json()
                logger.info(f"Arama başarılı. Kullanıcı: {request.session.get('username')}, Sonuç sayısı: {len(diaries)}")
            else:
                logger.error(f"API arama hatası. Durum Kodu: {response.status_code}")
                messages.error(request, f"API Hatası: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Arama bağlantı hatası: {str(e)}")
            messages.error(request, f"Bağlantı hatası: {str(e)}")

    return render(request, 'frontenddiaryapp/searchresults.html', {'diaries': diaries, 'query': query})


def profile_view(request):
    access_token = request.session.get('access_token')
    if not access_token:
        logger.warning('Yetkisiz profil görüntüleme denemesi.')
        messages.error(request, 'Profil bilgilerini görüntülemek için önce giriş yapmalısınız.')
        return redirect('login-view')

    headers = {'Authorization': f'Bearer {access_token}'}
    api_url = 'http://127.0.0.1:8000/diary/api/profile/'

    if request.method == 'POST':
        data = {
            'username': request.POST.get('username'),
            'email': request.POST.get('email'),
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'age': request.POST.get('age'),
            'phone': request.POST.get('phone'),
            'bio': request.POST.get('bio'),
            'gender': request.POST.get('gender'),
            'birth_date': request.POST.get('birth_date'),
            'location': request.POST.get('location'),
        }
        try:
            logger.info(f'Profil güncelleme denemesi: Kullanıcı={request.session.get("username")}')
            response = requests.put(api_url, headers=headers, json=data, timeout=5)
            if response.status_code == 200:
                logger.info(f'Profil başarıyla güncellendi: Kullanıcı={request.session.get("username")}')
                messages.success(request, 'Profil bilgileri başarıyla güncellendi.')
                return redirect('frontenddiaryapp:profile-view')
            else:
                logger.error(f'Profil güncelleme hatası: Durum Kodu={response.status_code}')
                messages.error(request, f"API Hatası: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f'Profil güncelleme bağlantı hatası: {str(e)}')
            messages.error(request, f'Bağlantı hatası: {str(e)}')

    try:
        logger.info(f'Profil verisi sorgulandı: Kullanıcı={request.session.get("username")}')
        response = requests.get(api_url, headers=headers, timeout=5)
        if response.status_code == 200:
            profile_data = response.json()
            return render(request, 'frontenddiaryapp/profile.html', {'profile': profile_data})
        else:
            logger.error(f'Profil verisi alınamadı: Durum Kodu={response.status_code}')
            messages.error(request, f"Profil verileri alınamadı: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f'Profil verisi bağlantı hatası: {str(e)}')
        messages.error(request, f'Bağlantı hatası: {str(e)}')

    return render(request, 'frontenddiaryapp/profile.html', {'profile': {}})


def profile_readonly_view(request):
    access_token = request.session.get('access_token')
    if not access_token:
        logger.warning('Yetkisiz profil görüntüleme denemesi (sadece okuma).')
        messages.error(request, 'Profil bilgilerini görüntülemek için giriş yapmalısınız.')
        return redirect('login-view')

    headers = {'Authorization': f'Bearer {access_token}'}
    api_url = 'http://127.0.0.1:8000/diary/api/profile/'

    try:
        logger.info(f'Profil (sadece okuma) verisi sorgulandı: Kullanıcı={request.session.get("username")}')
        response = requests.get(api_url, headers=headers, timeout=5)
        if response.status_code == 200:
            profile_data = response.json()
            return render(request, 'frontenddiaryapp/profile_readonly.html', {'profile': profile_data})
        else:
            logger.error(f'Profil (sadece okuma) verisi alınamadı: Durum Kodu={response.status_code}')
            messages.error(request, f"Profil verileri alınamadı: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f'Profil (sadece okuma) bağlantı hatası: {str(e)}')
        messages.error(request, f'Bağlantı hatası: {str(e)}')

    return render(request, 'frontenddiaryapp/profile_readonly.html', {'profile': {}})

