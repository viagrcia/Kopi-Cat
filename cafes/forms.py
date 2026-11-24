from django import forms
from django.core.files.uploadedfile import UploadedFile

from .models import JournalEntry

MAX_PHOTO_BYTES = 5 * 1024 * 1024


class EntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['cafe', 'title', 'visited_on', 'rating', 'note', 'photo']
        widgets = {
            'visited_on': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'rating': forms.Select(choices=[('', 'No rating')] + [(i, '★' * i) for i in range(1, 6)]),
            'note': forms.Textarea(attrs={'rows': 4}),
            'photo': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = False
        self.fields['cafe'].empty_label = 'Pick a cafe from the map'

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if isinstance(photo, UploadedFile) and photo.size > MAX_PHOTO_BYTES:
            raise forms.ValidationError('Please choose a photo under 5 MB.')
        return photo

    def clean(self):
        data = super().clean()
        if not data.get('title') and data.get('cafe'):
            data['title'] = data['cafe'].name
        if not data.get('title'):
            self.add_error('title', 'Pick a cafe or type a name.')
        return data


class StripForm(forms.Form):
    image = forms.ImageField()