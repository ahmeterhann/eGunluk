Projeyi çalıştırmak için öncelikle;
FinalProje dizininde python -m venv venv komutuyla bir sanal ortam oluşturun, 
ardından Windows için venv\Scripts\activate, Mac/Linux için ise source venv/bin/activate komutuyla sanal ortamı aktif hale getirin. 
Daha sonra pip install -r requirements.txt komutunu çalıştırarak tüm bağımlılıkları yükleyin. 
Ardından backend dizinine geçip python manage.py runserver komutuyla backend sunucusunu, 
frontend dizinine geçip python manage.py runserver 8001 komutuyla frontend sunucusunu çalıştırabilirsiniz. 
Tarayıcıdan http://127.0.0.1:8001/ adresine giderek uygulamayı kullanabilirsiniz.

## Kurulum

1. FinalProje dizininde sanal ortam oluşturun `python -m venv venv`  
2. Sanal ortamı aktif et:  
   - Windows: `venv\Scripts\activate`  
   - Mac/Linux: `source venv/bin/activate`  
3. Paketleri yükle: `pip install -r requirements.txt`  
4. backend dizininde: `python manage.py runserver`  
5. frontend dizininde: `python manage.py runserver 8001`  

## Kullanım

Tarayıcıda `http://127.0.0.1:8001/` adresini açın.