
from django import forms
from .models import Review

STAR_CHOICES = [(opt, str(opt)) for opt in range(1, 6)]


class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1, max_value=5, widget=forms.RadioSelect(choices=STAR_CHOICES), label="Calificación")

    comment = forms.CharField(widget=forms.Textarea(
        attrs={"rows": 4, "placeholder": "Cuéntanos tu experiencia..."}), required=False, label="Comentario")

    class Meta:
        model = Review
        fields = ("rating", "comment")

    def clean_rating(self):
        rating = self.cleaned_data["rating"]
        if not 1 <= rating <= 5:
            raise forms.ValidationError(
                "La calificación debe estar entre 1 y 5.")
        return rating
