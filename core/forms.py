from django import forms
from django.core.exceptions import ValidationError


class UploadForm(forms.Form):
    url = forms.URLField(max_length=1023, label="Image URL")
    img_file = forms.FileField(label="Upload from file: ")

    def clean(self):
        clean_data = super().clean()
        url = clean_data.get('url', None)
        img = clean_data.get('img_file', None)
        if not url and not img:
            raise ValidationError(
                "At least one of two fields must be filled")
        if url and img:
            raise ValidationError("Only one of two fields must be filled")
