
from django.urls import path
from .views import UserLoginView, UserSignupView, NoteCreateView, NoteDetailView, NoteShareView, NoteVersionHistoryView, NoteUpdate



urlpatterns = [
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('signup/', UserSignupView.as_view(), name='user-signup'),
    path('notes/create/', NoteCreateView.as_view(), name='note-create'),
    path('notes/<int:pk>/', NoteDetailView.as_view(), name='note-detail'),
    path('notes/share/', NoteShareView.as_view(), name='note-share'),
    path('notes/version-history/<int:id>/', NoteVersionHistoryView.as_view(), name='note-version-history'),
    path('notes/<int:pk>/', NoteDetailView.as_view(), name='note-detail'),
]