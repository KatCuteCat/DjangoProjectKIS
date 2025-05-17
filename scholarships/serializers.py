from rest_framework import serializers
from .models import Student, StipendType, StipendApplication, ApplicationHistory, AdminProfile
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Student
        fields = '__all__'


class AdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = AdminProfile
        fields = '__all__'


class StipendTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StipendType
        fields = '__all__'


class StipendApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StipendApplication
        fields = '__all__'
        read_only_fields = ['created_at', 'reviewed_at', 'reviewer']


class ApplicationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationHistory
        fields = '__all__'
        read_only_fields = ['timestamp']