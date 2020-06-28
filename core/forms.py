from django import forms
from django.core.exceptions import ValidationError


class UploadForm(forms.Form):
    url = forms.URLField(
        max_length=1023,
        label="Image URL",
        required=False
    )
    img_file = forms.ImageField(label="Upload from file", required=False)

    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data.get('url', None)
        img = cleaned_data.get('img_file', None)

        # validating that one one file source is filled
        if not url and not img:
            raise ValidationError(
                "At least one of two fields must be filled",
                code='invalid'
            )
        if url and img:
            raise ValidationError(
                "Only one of two fields must be filled",
                code='invalid'
            )
