from django import forms
from .models import Story, Segment


class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ('title', 'description', 'genre', 'cover')
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'عنوان داستانت چی باشه؟',
                'class': 'input-focus w-full bg-cream/50 border border-gold/30 rounded-xl px-4 py-3 text-sm',
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'یه خلاصه کوتاه... (اختیاری)',
                'rows': 3,
                'class': 'input-focus w-full bg-cream/50 border border-gold/30 rounded-xl px-4 py-3 text-sm resize-none',
            }),
            'genre': forms.Select(attrs={
                'class': 'input-focus w-full bg-cream/50 border border-gold/30 rounded-xl px-4 py-3 text-sm',
            }),
            'cover': forms.FileInput(attrs={
                'class': 'w-full text-sm text-ink/60 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:bg-wine file:text-cream file:text-sm',
                'accept': 'image/*',
            }),
        }


def count_letters(text):
    """شمارش فقط حروف (فارسی، انگلیسی و عربی)"""
    return sum(1 for c in text if c.isalpha())


class SegmentForm(forms.ModelForm):
    """فرم نوشتن ادامه داستان"""
    
    class Meta:
        model = Segment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': 'ادامه داستان رو اینجا بنویس... (حداکثر ۲۰۰۰ کاراکتر)',
                'rows': 6,
                'maxlength': 2000,
                'class': 'input-focus w-full bg-cream/50 border border-gold/30 rounded-xl px-4 py-3 text-sm resize-none',
            }),
        }

    def clean_text(self):
        text = self.cleaned_data.get('text', '').strip()
        
        if len(text) > 2000:
            raise forms.ValidationError('ادامه نباید بیشتر از ۲۰۰۰ کاراکتر باشه.')
        
        letters = count_letters(text)
        if letters < 20:
            raise forms.ValidationError(
                f'ادامه باید حداقل ۲۰ حرف داشته باشه. الان فقط {letters} حرف داری.'
            )
        
        return text