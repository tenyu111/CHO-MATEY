from django import forms
from datetime import datetime
from django.contrib.auth.forms import (
  UserCreationForm, UserChangeForm,
  PasswordChangeForm,AuthenticationForm
  )
from django.contrib.auth import get_user_model
from .models import Posts, Product_Categories, Products, Reactions, Results
from django.core.exceptions import ValidationError
import re,unicodedata


#新規登録
class CustomUserCreationForm(UserCreationForm):
      def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'ユーザー名', 'maxlength': 64})
        self.fields['password1'].widget.attrs.update({'placeholder': 'パスワード'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'パスワード再入力'})
      
      class Meta:
        model = get_user_model() #カスタムユーザーモデルを使用
        fields = ('username','password1','password2')
      
      def clean_username(self):
        username = self.cleaned_data['username']
        if get_user_model().objects.filter(username=username).exists():
            raise ValidationError('このユーザー名は既に使用されています。')
        return username
  
 
#ログイン 
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'ユーザー名'})
        self.fields['password'].widget.attrs.update({'placeholder': 'パスワード'})
    
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)

    def get_invalid_login_error(self):
        return forms.ValidationError(
            ("ログインに失敗しました"),
            code='invalid_login',
            params={'username': self.cleaned_data.get('username')},
        )
           
         
#投稿作成・編集・同じ商品の投稿検索用
class PostForm(forms.ModelForm):
   category = forms.ModelChoiceField(
      queryset=Product_Categories.objects.all(), required=False
    )
   image = forms.ImageField(required=False)
   product_name = forms.CharField(max_length=256, required=False)
   jan_code = forms.CharField(
    widget=forms.TextInput(attrs={'placeholder': '数字13桁のコードを入力'}),
    max_length=13,
    required=False
    )
   asin_code=forms.CharField(
    widget=forms.TextInput(attrs={'placeholder': '英数字10桁のコードを入力'}),
    max_length=10,
    required=False)
   purchase_place = forms.CharField(max_length=200, required=False)
   price = forms.IntegerField(min_value=0, required=False)
   purchase_reason = forms.CharField(widget=forms.Textarea(attrs={'maxlength': '400','placeholder':'400字以内で入力'}), required=False)
   
   def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.id:  # 既存の投稿を編集する場合
            self.fields['product_name'].initial = self.instance.product.product_name
            self.fields['category'].initial = self.instance.product.category
            self.fields['jan_code'].initial = self.instance.product.jan_code
            self.fields['asin_code'].initial = self.instance.product.asin_code
            
   class Meta:
     model = Posts
     fields = ['product_name','jan_code','asin_code','category','image', 'purchase_place', 'price', 'purchase_reason']
    
   def clean_jan_code(self):
      jan_code = self.cleaned_data.get('jan_code')
      if jan_code:
        #全角を半角に変換
        jan_code = unicodedata.normalize('NFKC', jan_code)
        # JANコードが数字のみで構成されているかを確認
        if not re.match(r'^\d+$', jan_code):
          raise ValidationError('JANコードは数字で構成される必要があります')
      return jan_code
    
   def clean_asin_code(self):
      asin_code = self.cleaned_data.get('asin_code')
      if asin_code:
        #全角を半角に変換
        asin_code = unicodedata.normalize('NFKC', asin_code)
          # ASINコードが英数字のみで構成されているかを確認
        if not re.match(r'^[0-9A-Za-z]{10}$', asin_code):
            raise forms.ValidationError('ASINコードは英数字で構成される必要があります')
      return asin_code
      
   def clean(self):
        cleaned_data = super().clean()
        product_name = cleaned_data.get('product_name')
        jan_code = cleaned_data.get('jan_code')
        asin_code = cleaned_data.get('asin_code')
        
         # 同じ商品の投稿検索における処理
        if 'preview' in self.data:
            if not (product_name or jan_code or asin_code):
                raise forms.ValidationError("商品名,JANコード,またはASINコードのどれかを入力してください。")
        # 投稿するにあたっての処理
        elif 'submit' in self.data:
            if not(jan_code or asin_code):
               self.add_error('jan_code', "JANコードまたはASINコードのどちらかを入力してください。")
               self.add_error('asin_code', "JANコードまたはASINコードのどちらかを入力してください。")

            required_fields = ['product_name', 'category', 'image', 'purchase_place', 'price', 'purchase_reason']
            missing_fields = [field for field in required_fields if not cleaned_data.get(field)]
            # if missing_fields:
            for field in missing_fields:
              if field not in cleaned_data or not cleaned_data[field]:
                    self.add_error(field, "このフィールドは必須です。")
                    
        return cleaned_data
      
   def save(self, commit=True):
        instance = super().save(commit=False)

        # 製品名とカテゴリを取得
        product_name = self.cleaned_data.get('product_name')
        jan_code = self.cleaned_data.get('jan_code')
        asin_code = self.cleaned_data.get('asin_code')
        category = self.cleaned_data.get('category')
        
        # 既存の製品を検索、なければ新規作成
        product, created = Products.objects.get_or_create(
          product_name=product_name, 
          jan_code = jan_code,
          asin_code = asin_code,
          category=category,
          )

        # 製品をポストインスタンスに関連付け
        instance.product = product
        
        if created:
          print("新しい商品が作成されました")

        if commit:
            instance.save()
        return instance


#結果報告用のフォーム
class ResultForm(forms.ModelForm):
  result_comment = forms.CharField(
    widget=forms.Textarea(attrs={'maxlength': '400','placeholder':'400字以内で入力'})
    )
  class Meta:
    model = Results
    fields = ['result_category','purchased_product_name','result_image','result_comment']
    

#ホーム画面での検索フォーム
class SearchForm(forms.Form):
    product_name = forms.CharField(
      required=False, label='',
      widget=forms.TextInput(attrs={'placeholder':'商品名','class':'form-control'})
      )
    category = forms.ModelChoiceField(
      queryset=Product_Categories.objects.all(),
      required=False,
      label='',
      empty_label='商品カテゴリ',
      widget=forms.Select(attrs={'class':'form-control'})
      )
    jan_code = forms.CharField(
      required=False, label='',
      widget=forms.TextInput(attrs={'placeholder':'JANコード','class':'form-control'}),
      max_length=13
      )
    asin_code = forms.CharField(
      required=False, label='',
      widget=forms.TextInput(attrs={'placeholder':'ASINコード','class':'form-control'}),
      max_length=10
      )

    def clean_jan_code(self):
      jan_code = self.cleaned_data.get('jan_code')
      if jan_code:
        #全角を半角に変換
        jan_code = unicodedata.normalize('NFKC', jan_code)
      return jan_code
    
    def clean_asin_code(self):
      asin_code = self.cleaned_data.get('asin_code')
      if asin_code:
        #全角を半角に変換
        asin_code = unicodedata.normalize('NFKC', asin_code)
      return asin_code
    
#投稿に対するリアクション用フォーム   
class ReactionForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
        super(ReactionForm, self).__init__(*args, **kwargs)
        self.fields['comment'].widget.attrs.update({'placeholder': 'コメントを入力(200字以内)'})
  class Meta:
    model = Reactions
    fields = ('comment','boost_score')
    widgets = {
      'boost_score': forms.NumberInput(attrs={'min':1, 'max':100})
    }
    
    
#ユーザ情報編集用フォーム（ユーザー名）
class CustomUserChangeForm(UserChangeForm):
  class Meta:
    model = get_user_model()
    fields = ('username',)
    widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'ユーザー名を入力'}),
        }
    
  def clean_username(self):
        username = self.cleaned_data['username']
        if get_user_model().objects.filter(username=username).exists():
            raise ValidationError('このユーザー名は既に使用されています。')
        return username

#ユーザ情報編集用フォーム（パスワード）
class CustomPasswordChangeForm(PasswordChangeForm):
   def __init__(self, *args, **kwargs):
        super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)
        del self.fields['old_password']
        self.fields['new_password1'].widget = forms.PasswordInput(attrs={'placeholder': '新しいパスワード'})
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={'placeholder': '新しいパスワード（確認用）'})