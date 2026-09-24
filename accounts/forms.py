from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import User


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        label='ایمیل',
        widget=forms.EmailInput(attrs={
            'placeholder': 'you@example.com',
            'class': 'input-focus w-full bg-cream/50 border border-gold/30 rounded-xl px-4 py-3 text-sm',
            'dir': 'ltr',
        })
    )
    username = forms.CharField(
        label='نام کاربری',
        widget=forms.TextInput(attrs={
            'placeholder': 'مثلاً: sara_writes',
            'class': 'input-focus w-full bg-cream/50 border border-gold/30 rounded-xl px-4 py-3 text-sm',
        })
    )
    password1 = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'حداقل ۸ کاراکتر',
            'class': 'input-focus w-full bg-cream/50 border border-gold/30 rounded-xl px-4 py-3 text-sm',
        })
    )
    password2 = forms.CharField(
        label='تکرار رمز عبور',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'دوباره وارد کن',
            'class': 'input-focus w-full bg-cream/50 border border-gold/30 rounded-xl px-4 py-3 text-sm',
        })
    )
    terms = forms.BooleanField(
        label='با قوانین و شرایط موافقم',
        required=True,
        error_messages={'required': 'برای ثبت‌نام باید قوانین را بپذیری'}
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('این ایمیل قبلاً ثبت شده است.')
        return email.lower()

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('این نام کاربری قبلاً گرفته شده.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='نام کاربری یا ایمیل',
        widget=forms.TextInput(attrs={
            'placeholder': 'نام کاربری یا ایمیل',
            'class': 'input-focus w-full bg-cream/50 border border-gold/30 rounded-xl px-4 py-3 text-sm',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'رمز عبور',
            'class': 'input-focus w-full bg-cream/50 border border-gold/30 rounded-xl px-4 py-3 text-sm',
        })
    )
    remember_me = forms.BooleanField(
        label='من رو به خاطر بسپار',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'w-4 h-4 accent-wine rounded'})
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            if '@' in username:
                try:
                    user_obj = User.objects.get(email__iexact=username)
                    username = user_obj.username
                except User.DoesNotExist:
                    pass
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise ValidationError('نام کاربری/ایمیل یا رمز عبور اشتباه است.', code='invalid_login')
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'bio', 'avatar', 'birth_date', 'favorite_genre')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input-focus w-full bg-cream/50 border border-gold/30 rounded-xl px-4 py-3 text-sm', 'placeholder': 'نام'}),
            'last_name': forms.TextInput(attrs={'class': 'input-focus w-full bg-cream/50 border border-gold/30 rounded-xl px-4 py-3 text-sm', 'placeholder': 'نام خانوادگی'}),
            'email': forms.EmailInput(attrs={'class': 'input-focus w-full bg-cream/50 border border-gold/30 rounded-xl px-4 py-3 text-sm', 'dir': 'ltr'}),
            'bio': forms.Textarea(attrs={'class': 'input-focus w-full bg-cream/50 border border-gold/30 rounded-xl px-4 py-3 text-sm resize-none', 'rows': 4, 'placeholder': 'درباره خودت...', 'maxlength': 500}),
            'avatar': forms.FileInput(attrs={'class': 'w-full text-sm text-ink/60 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:bg-wine file:text-cream file:text-sm', 'accept': 'image/*'}),
            'birth_date': forms.DateInput(attrs={'class': 'input-focus w-full bg-cream/50 border border-gold/30 rounded-xl px-4 py-3 text-sm', 'type': 'date'}),
            'favorite_genre': forms.TextInput(attrs={'class': 'input-focus w-full bg-cream/50 border border-gold/30 rounded-xl px-4 py-3 text-sm', 'placeholder': 'مثلاً: معمایی'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('این ایمیل قبلاً ثبت شده است.')
        return email