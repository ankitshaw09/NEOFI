
from rest_framework import serializers
from .models import Note,NoteVersion,NoteUpdate
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'owner', 'shared_with']

class NoteVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteVersion
        fields = ['content', 'updated_at']

class NoteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteUpdate
        fields = ['content', 'updated_at']
