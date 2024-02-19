
from django.shortcuts import get_object_or_404
from rest_framework import status,generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Note, SharedNote,NoteVersion,NoteUpdate
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .serializers import NoteSerializer, NoteVersionSerializer, UserSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view

@api_view(['POST'])
def create_user(request):

    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    user = User.objects.create_user(username=username, email=email, password=password)

    # Generate and save a token for the new user
    token, created = Token.objects.get_or_create(user=user)

    

class UserSignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]  # Allow any user (even unauthenticated) to register

    def perform_create(self, serializer):
        user = serializer.save()
        Token.objects.create(user=user)  # Generate and save a token for the new user

class UserLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = token.user
        return Response({'token': token.key, 'user_id': user.id, 'username': user.username})


class NoteCreateView(generics.CreateAPIView):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class NoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Note.objects.filter(models.Q(owner=user) | models.Q(shared_with=user)).distinct()

    def perform_update(self, serializer):
        old_content = serializer.instance.content
        new_content = self.request.data.get('content')

        if old_content != new_content:
            NoteUpdate.objects.create(note=serializer.instance, content=old_content)

        serializer.save()

class NoteShareView(generics.UpdateAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        note = serializer.instance
        user_ids = self.request.data.get('user_ids', [])
        
        # Ensure that the current user is the owner of the note
        if note.owner != self.request.user:
            return Response({'detail': 'You do not have permission to share this note.'}, status=403)

        # Add shared users to the note
        shared_users = User.objects.filter(id__in=user_ids)
        note.shared_with.set(shared_users)

        serializer.save()
        return Response({'detail': 'Note shared successfully.'})



class NoteVersionHistoryView(generics.ListAPIView):
    serializer_class = NoteVersionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        note_id = self.kwargs['id']

        # Check if the user has access to the note
        if not Note.objects.filter(id=note_id, owner=user).exists() and not Note.objects.filter(id=note_id, shared_with=user).exists():
            return NoteVersion.objects.none()

        # Retrieve version history
        note_updates = NoteUpdate.objects.filter(note_id=note_id).order_by('updated_at')
        version_history = []

        for update in note_updates:
            version_history.append({
                'timestamp': update.updated_at,
                'user': update.note.owner.username,
                'changes': update.content,
            })

        return version_history