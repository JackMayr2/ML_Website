from django import forms
from articles.models import Article
from django.core.files.uploadedfile import InMemoryUploadedFile
from learnings.humanize import naturalsize


class CommentForm(forms.Form):
    comment = forms.CharField(required=True, max_length=500, min_length=3, strip=True)
