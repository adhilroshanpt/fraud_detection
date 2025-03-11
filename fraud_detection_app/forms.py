from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1','password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'user' 
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UserLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if user.user_type != 'user':
            raise forms.ValidationError(
                "This account is not a user account.",
                code='invalid_user_type',
            )
        
class AdminLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if user.user_type != 'admin':
            raise forms.ValidationError(
                "This account is not a admin account.",
                code='invalid_user_type',
            )