from django import forms
from datetime import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


class CustomUserCreationForm(UserCreationForm):
      def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
        self.fields['password1'].label = 'パスワード'
        self.fields['password2'].label = 'パスワード再入力'
    
      class Meta:
        model = get_user_model()  # カスタムユーザーモデルを使用
        fields = ('username','password1','password2')
        widgets = {
            'username': forms.TextInput(attrs={'maxlength': 64}),
            'password1': forms.PasswordInput(attrs={'maxlength': 64}),
            'password2': forms.PasswordInput(attrs={'maxlength': 64}),
        }
        labels={
            'username':'ユーザー名',
        }
        
      def save(self, *args, **kwargs):
        obj = super(CustomUserCreationForm, self).save(commit=False)
        obj.created_at = datetime.now()
        obj.updated_at = datetime.now()
        obj.save()
        return obj