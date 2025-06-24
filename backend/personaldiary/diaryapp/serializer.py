from diaryapp.models import Diary
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from diaryapp.models import Profile

# Kullanıcı kayıt için serializer
class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Bu kullanıcı adı zaten kayıtlı.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

# Kullanıcı giriş için serializer
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Geçersiz kullanıcı adı veya şifre.")
        data['user'] = user
        return data
    

class DiarySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=100)
    content = serializers.CharField()
    date = serializers.DateField()
    created_at = serializers.DateTimeField(read_only=True)
    
    # user'ı read_only tutuyoruz, view'de otomatik set edeceğiz
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    def create(self, validated_data):
        user = self.context['request'].user
        diary = Diary.objects.create(user=user, **validated_data)
        return diary
    



    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.date = validated_data.get('date', instance.date)
        instance.save()
        return instance




class ProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(allow_blank=True, required=False, source='user.first_name')
    last_name = serializers.CharField(allow_blank=True, required=False, source='user.last_name')
    age = serializers.IntegerField(required=False)
    phone = serializers.CharField(allow_blank=True, required=False)
    username = serializers.CharField(source='user.username', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    bio = serializers.CharField(allow_blank=True, required=False)
    gender = serializers.CharField(allow_blank=True, required=False)
    birth_date = serializers.DateField(required=False)
    location = serializers.CharField(allow_blank=True, required=False)

    
    def to_representation(self, instance):
        return {
            "username": instance.user.username,
            "email": instance.user.email,
            "first_name": instance.user.first_name,
            "last_name": instance.user.last_name,
            "age": instance.age,
            "phone": instance.phone,
            "bio": instance.bio,
            "gender": instance.gender,
            "birth_date": instance.birth_date,
            "location": instance.location,
        }

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})

        instance.age = validated_data.get('age', instance.age)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.birth_date = validated_data.get('birth_date', instance.birth_date)
        instance.location = validated_data.get('location', instance.location)
        instance.save()
        
        user = instance.user
        user.username = user_data.get('username', user.username)
        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        user.email = user_data.get('email', user.email)
        user.save()
        
        return instance



    
