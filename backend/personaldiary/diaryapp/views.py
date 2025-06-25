from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from .serializer import UserRegisterSerializer, UserLoginSerializer
from rest_framework import generics, permissions
from .models import Diary
from .serializer import DiarySerializer
from django.shortcuts import get_object_or_404 
from django.db.models import Q
from .models import Profile
from .serializer import ProfileSerializer
from django.contrib.auth.models import User
import logging
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from django.http import Http404





logger = logging.getLogger(__name__)

class RegisterView(APIView):
    def post(self, request):
        try:
            logger.info("RegisterView POST method çağrıldı.")
            serializer = UserRegisterSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Yeni kullanıcı oluşturuldu: {serializer.data.get('email')}")
                return Response({'message': 'Kullanıcı başarıyla oluşturuldu.'}, status=status.HTTP_201_CREATED)
            
            logger.warning(f"Kayıt validation hatası: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError as e:
            logger.error(f"Veritabanı hatası (muhtemelen tekrar eden kullanıcı): {str(e)}")
            return Response({'error': 'Bu e-posta zaten kayıtlı.'}, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            logger.error(f"Doğrulama hatası: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception("Kayıt sırasında beklenmeyen bir hata oluştu.")
            return Response({'error': 'Sunucu hatası oluştu. Lütfen daha sonra tekrar deneyin.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    def post(self, request):
        try:
            logger.info("LoginView POST method çağrıldı.")
            serializer = UserLoginSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data['user']
                refresh = RefreshToken.for_user(user)
                logger.info(f"Kullanıcı giriş yaptı: {user.username}")
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            
            logger.warning(f"Giriş validation hatası: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception("Giriş sırasında beklenmeyen bir hata oluştu.")
            return Response({'error': 'Sunucu hatası oluştu. Lütfen daha sonra tekrar deneyin.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class DiaryListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            logger.info(f"DiaryListCreateView GET method çağrıldı. Kullanıcı: {request.user.username}")
            diaries = Diary.objects.filter(user=request.user)
            serializer = DiarySerializer(diaries, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Günlük listeleme sırasında hata oluştu.")
            return Response({'error': 'Günlükler listelenirken sunucu hatası oluştu.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            logger.info(f"DiaryListCreateView POST method çağrıldı. Kullanıcı: {request.user.username}")
            serializer = DiarySerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Yeni günlük kaydı oluşturuldu. Kullanıcı: {request.user.username}, Günlük ID: {serializer.data.get('id')}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            logger.warning(f"Günlük oluşturma validation hatası: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Günlük oluşturulurken hata oluştu.")
            return Response({'error': 'Günlük oluşturulurken sunucu hatası oluştu.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class DiaryRetrieveUpdateDestroyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        try:
            diary = get_object_or_404(Diary, pk=pk, user=user)
            return diary
        except Exception as e:
            logger.error(f"Diary nesnesi bulunamadı veya erişim engellendi: pk={pk}, user={user}. Hata: {str(e)}")
            raise

    def get(self, request, pk):
        try:
            logger.info(f"DiaryRetrieveUpdateDestroyView GET çağrıldı. Kullanıcı: {request.user.username}, Günlük ID: {pk}")
            diary = self.get_object(pk, request.user)
            serializer = DiarySerializer(diary)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            return Response({'error': 'Günlük bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            logger.exception("Diary GET işlemi sırasında beklenmeyen hata.")
            return Response({'error': 'Sunucu hatası oluştu.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            logger.info(f"DiaryRetrieveUpdateDestroyView PUT çağrıldı. Kullanıcı: {request.user.username}, Günlük ID: {pk}")
            diary = self.get_object(pk, request.user)
            serializer = DiarySerializer(diary, data=request.data)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Günlük güncellendi. Kullanıcı: {request.user.username}, Günlük ID: {pk}")
                return Response(serializer.data)
            logger.warning(f"Günlük güncelleme validation hatası: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            return Response({'error': 'Günlük bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            logger.exception("Diary PUT işlemi sırasında beklenmeyen hata.")
            return Response({'error': 'Sunucu hatası oluştu.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, pk):
        try:
            logger.info(f"DiaryRetrieveUpdateDestroyView PATCH çağrıldı. Kullanıcı: {request.user.username}, Günlük ID: {pk}")
            diary = self.get_object(pk, request.user)
            serializer = DiarySerializer(diary, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Günlük kısmi olarak güncellendi. Kullanıcı: {request.user.username}, Günlük ID: {pk}")
                return Response(serializer.data)
            logger.warning(f"Günlük kısmi güncelleme validation hatası: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            return Response({'error': 'Günlük bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            logger.exception("Diary PATCH işlemi sırasında beklenmeyen hata.")
            return Response({'error': 'Sunucu hatası oluştu.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            logger.info(f"DiaryRetrieveUpdateDestroyView DELETE çağrıldı. Kullanıcı: {request.user.username}, Günlük ID: {pk}")
            diary = self.get_object(pk, request.user)
            diary.delete()
            logger.info(f"Günlük silindi. Kullanıcı: {request.user.username}, Günlük ID: {pk}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response({'error': 'Günlük bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            logger.exception("Diary DELETE işlemi sırasında beklenmeyen hata.")
            return Response({'error': 'Sunucu hatası oluştu.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DiarySearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            query = request.query_params.get('q', '')  # ?q=aramaTerimi
            logger.info(f"DiarySearchView GET çağrıldı. Kullanıcı: {request.user.username}, Arama: '{query}'")

            if query:
                diaries = Diary.objects.filter(
                    Q(user=request.user) & (
                        Q(title__icontains=query) |
                        Q(content__icontains=query)
                    )
                )
            else:
                diaries = Diary.objects.filter(user=request.user)

            serializer = DiarySerializer(diaries, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            logger.exception("DiarySearchView GET işlemi sırasında beklenmeyen hata.")
            return Response({'error': 'Sunucu hatası oluştu.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            logger.info(f"ProfileView GET çağrıldı. Kullanıcı: {request.user.username}")
            profile = Profile.objects.get(user=request.user)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            logger.warning(f"Profil bulunamadı. Kullanıcı: {request.user.username}")
            return Response({'detail': 'Profil bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            logger.exception("ProfileView GET işlemi sırasında beklenmeyen hata.")
            return Response({'error': 'Sunucu hatası oluştu.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            logger.info(f"ProfileView PUT çağrıldı. Kullanıcı: {request.user.username}")
            profile = Profile.objects.get(user=request.user)
            serializer = ProfileSerializer(profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Profil güncellendi. Kullanıcı: {request.user.username}")
                return Response(serializer.data)
            logger.warning(f"Profil güncelleme validation hatası: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            logger.warning(f"Profil bulunamadı. Kullanıcı: {request.user.username}")
            return Response({'detail': 'Profil bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            logger.exception("ProfileView PUT işlemi sırasında beklenmeyen hata.")
            return Response({'error': 'Sunucu hatası oluştu.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

