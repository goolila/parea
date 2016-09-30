from django import forms
from conference.models import Event, Paper, Profile, Review


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'acronym']

class PaperForm(forms.ModelForm):
    class Meta:
        model = Paper
        fields = ['title', 'abstract', 'event', 'paper_file']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user', 'password', 'user_type')

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review

        fields = ['decision', 'rate', 'comment']
