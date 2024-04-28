from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import  PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .forms import(
    CustomUserCreationForm, 
    CustomAuthenticationForm,
    PostForm, ResultForm,SearchForm, 
    ReactionForm, CustomUserChangeForm,
    CustomPasswordChangeForm
    )
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .models import Posts, Liked_Posts, Results, Reactions
from django.http import JsonResponse
from django.views import View


#スタート画面
def start(request):
    return render(request, 'start.html')


#新規登録
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


#ログイン
class CustomLoginView(LoginView):
    template_name='login.html'
    form_class = CustomAuthenticationForm
    def get_success_url(self):
        return reverse_lazy('home')  


#ログアウト
class LogoutConfirmView(View):
    def get(self, request):
        return render(request, 'logout_confirm.html')

    def post(self, request):
        # 「はい」が選択された場合、ログアウトを実行
        if 'confirm' in request.POST:
            logout(request)
            return redirect('start')  # ログアウト後のリダイレクト先
        return redirect('home')  # 「いいえ」の場合、ホームに戻る


#ヘルパー関数（投稿一覧を表示する際に適用）
def enrich_post_with_likes_and_results(posts, user):
    posts_with_likes = []
    for post in posts:
        liked_count = Liked_Posts.objects.filter(post=post).count()
        result = Results.objects.filter(post=post).first()
        has_result = result is not None
        liked = Liked_Posts.objects.filter(post=post, user=user).exists()
        posts_with_likes.append({
            'post': post,
            'liked_count': liked_count,
            'liked': liked,
            'result': result,
            'has_result': has_result,
        })
    return posts_with_likes


#ホーム画面（検索機能つき）   
@login_required    
def home(request):
    #検索機能
     search_form = SearchForm(request.GET or None)
     if search_form.is_valid():
         product_name = search_form.cleaned_data.get('product_name')
         category = search_form.cleaned_data.get('category')
         jan_code = search_form.cleaned_data.get('jan_code')

         posts = Posts.objects.all().order_by('-updated_at')
         if product_name:
             posts = posts.filter(product__product_name__icontains=product_name)
         if category:
             posts = posts.filter(product__category=category)
         if jan_code:
             posts = posts.filter(product__jan_code__icontains=jan_code)
     else:
        posts = Posts.objects.all().order_by('-updated_at')
     
     posts_with_likes = enrich_post_with_likes_and_results(posts, request.user)
        
     return render(request, 'home.html', {
         'search_form': search_form, 
         'posts_with_likes':posts_with_likes,
         })


#投稿詳細
@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Posts, pk=post_id)
    liked = False
    liked_count = Liked_Posts.objects.filter(post=post).count()
    result = Results.objects.filter(post=post).first()
    reactions = Reactions.objects.filter(post=post).order_by('-created_at')
    
    if request.user.is_authenticated:
        liked = Liked_Posts.objects.filter(post=post, user=request.user).exists()
    
    #投稿に対するリアクション
    reaction_form = None
    if not result:    
     if request.method == "POST":
        reaction_form = ReactionForm(request.POST)
        if reaction_form.is_valid():
          if request.user.is_authenticated:
            reaction = reaction_form.save(commit=False)
            reaction.user = request.user
            reaction.post = post
            reaction.save()
        return redirect('post_detail', post_id=post_id)
     else:
        reaction_form = ReactionForm()
        
    return render(request, 'post_detail.html', {
        'post': post,
        'reactions': reactions,
        'reaction_form': reaction_form,
        'liked': liked,
        'liked_count': liked_count,
        'result': result,
        })


#投稿に対するリアクションを削除
@login_required
def delete_reaction(request, reaction_id):
    reaction = get_object_or_404(Reactions, id=reaction_id, user=request.user)  # ユーザーが所有するコメントを取得
    post_id = reaction.post.id
    if request.method == 'POST':
        reaction.delete()
    return redirect('post_detail',post_id=post_id)


#いいね機能
@login_required
def liked_post(request):
    post_pk = request.POST.get('post_pk')
    post = get_object_or_404(Posts, pk=post_pk)
    liked  =Liked_Posts.objects.filter(post=post,user=request.user)
    context={}
    if liked.exists():
        liked.delete()
        context['method'] = 'delete'
    else:
        liked.create(post=post, user=request.user)
        context['method'] = 'create'
    context['liked_count'] = Liked_Posts.objects.filter(post=post).count()
    return JsonResponse(context)


#いいねした投稿一覧
@login_required
def liked_posts_view(request):
    liked_post_ids = Liked_Posts.objects.filter(user=request.user).values_list('post_id', flat=True)
    posts = Posts.objects.filter(id__in=liked_post_ids).order_by('-updated_at')

    posts_with_likes = enrich_post_with_likes_and_results(posts, request.user)
    
    return render(request, 'liked_posts_view.html', {'posts_with_likes': posts_with_likes})


#マイページ
@login_required    
def mypage(request):
      user = request.user 
      if user.is_authenticated:
        own_posts = Posts.objects.filter(user=user).order_by('-updated_at')
        posts_with_likes = enrich_post_with_likes_and_results(own_posts, request.user)
    
        context = {'posts_with_likes': posts_with_likes}

      return render(request, 'mypage.html', context)


#投稿作成・同じ商品の投稿表示
@login_required
def create_post(request):
    form = PostForm(request.POST or None, request.FILES or None)
    related_posts_info = None
    preview_clicked = False
    
    if request.method == 'POST':
        #同じ商品の投稿表示
        if 'preview' in request.POST:
            preview_clicked = True
            if form.is_valid():
                product_name = form.cleaned_data.get('product_name')
                jan_code = form.cleaned_data.get('jan_code')
                related_posts_query = Posts.objects.filter(product__product_name=product_name) | Posts.objects.filter(product__jan_code=jan_code)
                related_posts_info = []
                for post in related_posts_query:
                    liked_count = Liked_Posts.objects.filter(post=post).count()
                    has_result = Results.objects.filter(post=post).exists()
                    related_posts_info.append({
                        'post': post,
                        'liked_count': liked_count,
                        'has_result': has_result,
                    })
                if not related_posts_info:
                    related_posts_info = []
        #新規投稿          
        elif 'submit' in request.POST:
            if form.is_valid():
                post = form.save(commit=False)
                post.user = request.user 
                post.save()
                return redirect('mypage')

    return render(request, 'create_post.html', {
        'form': form,
        'related_posts': related_posts_info,
        'preview_clicked' : preview_clicked
    })


#投稿編集・削除
@login_required
def edit_delete_post(request, post_id):
    post = get_object_or_404(Posts, id=post_id, user=request.user)  # ユーザーが所有する投稿を取得
    show_edit_links = request.user.is_authenticated and post.user == request.user
    
    if request.method == 'POST':
        if 'delete' in request.POST:  # 削除ボタンが押された場合
            post.delete()
            return redirect('mypage')
        else:  # 編集の場合
            form = PostForm(request.POST, request.FILES, instance=post)
            if form.is_valid():
                form.save()
                return redirect('mypage')
    else:
        form = PostForm(instance=post)

    return render(request, 'edit_delete_post.html', {
        'form': form,
        'post': post,
        'show_edit_links':show_edit_links
    })


#結果報告
@login_required
def report_result(request, post_id):
    post = get_object_or_404(Posts, pk=post_id, user=request.user)
    liked = Liked_Posts.objects.filter(post=post, user=request.user).exists()
    liked_count = Liked_Posts.objects.filter(post=post).count()
    
    if request.method == 'POST':
        form = ResultForm(request.POST, request.FILES)
        if form.is_valid():
            result = form.save(commit=False)
            result.post = post
            result.save()
            return redirect('mypage')
    else:
        form = ResultForm()  

    return render(request, 'report_result.html', {
        'form': form,
        'post': post,
        'liked': liked,
        'liked_count':liked_count,
    })


#結果編集
@login_required
def edit_result(request, post_id, result_id):
    post = get_object_or_404(Posts, pk=post_id, user=request.user)
    liked = Liked_Posts.objects.filter(post=post, user=request.user).exists()
    liked_count = Liked_Posts.objects.filter(post=post).count()
    result = get_object_or_404(Results, id=result_id, post=post)
    
    if request.method == 'POST':
        if 'delete' in request.POST:
            result.delete()
            return redirect('mypage')
        else:
            form = ResultForm(request.POST, request.FILES, instance=result)
            if form.is_valid():
                form.save()
                return redirect('mypage')
    else:
        form = ResultForm(instance=result)
        
    return render(request, 'edit_result.html', {
        'form': form,
        'post': post,
        'liked': liked,
        'liked_count':liked_count,
        'result':result,
    })


#ユーザー情報編集
@login_required
def edit_profile(request):
      if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, instance=request.user)
        password_form = CustomPasswordChangeForm(request.user, request.POST)
        if user_form.is_valid() and password_form.is_valid():
            user_form.save()
            password_form.save()
            update_session_auth_hash(request, request.user)
            return redirect('mypage')  
      else:
           user_form = CustomUserChangeForm(instance=request.user)
           password_form = CustomPasswordChangeForm(request.user)
           
      return render(request, 'edit_profile.html', {
          'user_form': user_form,
          'password_form':password_form,
          })
