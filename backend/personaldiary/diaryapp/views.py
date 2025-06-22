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





class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Kullanıcı başarıyla oluşturuldu.'}, status=status.HTTP_201_CREATED)
        print(serializer.errors)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DiaryListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        diaries = Diary.objects.filter(user=request.user)
        serializer = DiarySerializer(diaries, many=True)
        return Response(serializer.data)

    def post(self, request):

        serializer = DiarySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()  
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DiaryRetrieveUpdateDestroyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        # Kullanıcının sadece kendi diary kaydına erişmesini sağlıyoruz
        return get_object_or_404(Diary, pk=pk, user=user)

    def get(self, request, pk):
        diary = self.get_object(pk, request.user)
        serializer = DiarySerializer(diary)
        return Response(serializer.data)

    def put(self, request, pk):
        diary = self.get_object(pk, request.user)
        serializer = DiarySerializer(diary, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        diary = self.get_object(pk, request.user)
        serializer = DiarySerializer(diary, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        diary = self.get_object(pk, request.user)
        diary.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class DiarySearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '')  # ?q=aramaTerimi
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
        return Response(serializer.data)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({'detail': 'Profil bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({'detail': 'Profil bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = request.user
            user.username = request.data.get('username', user.username)
            user.email = request.data.get('email', user.email)
            user.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)