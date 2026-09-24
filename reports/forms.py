from django import forms
from .models import Report


class ReportForm(forms.Form):
    """فرم گزارش محتوا"""
    
    reason = forms.ChoiceField(
        label='دلیل گزارش',
        choices=Report.REASON_CHOICES,
        widget=forms.Select(attrs={
            'class': 'input-focus w-full bg-cream/50 border border-gold/30 rounded-xl px-4 py-3 text-sm',
        })
    )
    
    description = forms.CharField(
        label='توضیحات (اختیاری)',
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={
            'placeholder': 'اگه توضیح بیشتری داری، اینجا بنویس...',
            'rows': 3,
            'maxlength': 500,
            'class': 'input-focus w-full bg-cream/50 border border-gold/30 rounded-xl px-4 py-3 text-sm resize-none',
        })
    )