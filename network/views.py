import json

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator

from .models import User, Post, Like
from .forms import PostForm
from .backends import authenticate_via_email

POSTS_PER_PAGE = 5

def index(request):
    all_posts = Post.objects.all()
    
    # If user is logged in then we can search for all liked posts by user
    liked_posts_by_user = set()
    if request.user.is_authenticated:
        liked_posts_by_user = set(Like.objects.filter(user=request.user).values_list('post_id', flat=True))
    
    # Each post will have is_liked value True/False   
    for post in all_posts:
        post.is_liked = post.id in liked_posts_by_user
    
    p = Paginator(all_posts, POSTS_PER_PAGE)
    page_num = request.GET.get("page")
    page_obj = p.get_page(page_num)
        
    return render(request, "network/index.html", context={
        "page_obj": page_obj,
        "post_form": PostForm()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username_or_email = request.POST["username"]
        password = request.POST["password"]
        
        user = authenticate(request, username=username_or_email, password=password)
        if user is None:
            user = authenticate_via_email(request, email=username_or_email, password=password)
        
        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("network:index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("network:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("network:index"))
    else:
        return render(request, "network/register.html")
    
    
@csrf_exempt
@login_required  
def create_post(request):   
    if "new_post" in request.POST:
        form = PostForm(request.POST)
        if form.is_valid():
            Post.objects.create(
                user=request.user,
                content=form.cleaned_data["content"])
    
    # It returns page from which form was sent or to home page
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "network:index"))


# API function for getting all posts
def all_posts(request):
    all_posts = Post.objects.all().order_by("-date_post").all()
    return JsonResponse([post.serialize() for post in all_posts], safe=False)


# API function for getting post, editing and deleting
def post(request, id):
    try:
        post = Post.objects.get(pk=id)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Post does not exist'}, status=404)
    
    if request.method == "GET":
        return JsonResponse([post.serialize()], safe=False)
    
    elif request.method == "DELETE" and post.user == request.user:
        post.delete()
        return JsonResponse({'message': f'Post {id=} is successfully deleted'}, status=200)
    
    elif request.method == "PUT" and post.user == request.user:
        old_content = post.content
        data = json.loads(request.body)
        if old_content == data["content"]:
            return JsonResponse({'error': 'Post content is same as original'}, status=404)
        else:
            post.content = data["content"]
            post.edited = True
            post.date_edit = datetime.now()
            post.save()
            return JsonResponse({'message': f'Post {id=} is successfully edited'}, status=200)
    
    else:
        return JsonResponse({'error': 'Method not supported'}, status=405)
    

# Function which gives information about network user
def user(request, username):
    try:
        user_db = User.objects.get(username=username)
        followers = user_db.followers.all()
        following = user_db.following.all()
        user_posts = user_db.posts.all()
        
        # If user is logged in then we can search for all liked posts by user
        liked_posts_by_user = set()
        if request.user.is_authenticated:
            liked_posts_by_user = set(Like.objects.filter(user=request.user).values_list('post_id', flat=True))
    
        # Each post will have is_liked value True/False   
        for post in user_posts:
            post.is_liked = post.id in liked_posts_by_user
        
        p = Paginator(user_posts, POSTS_PER_PAGE)
        page_num = request.GET.get("page")
        page_obj = p.get_page(page_num)
        
        # If visiting request.user is following this 
        followee = request.user and request.user != user_db and followers.filter(id=request.user.id).exists() 
        
        return render(request, "network/user.html", context={
            "username": username,
            "error": False,
            "page_obj": page_obj,
            "following": followee,
            "num_posts": len(user_posts),
            "num_followers": len(followers),
            "num_following": len(following),
            "post_form": PostForm()
        })

    except:
        return render(request, "network/user.html", context={
            "username": username,
            "error": True,
        })    
    

# user1 is following user2
@login_required 
@csrf_exempt
def follow(request, username):
    user1 = request.user
    
    try:
        user2 = User.objects.get(username=username)
    except:
        return JsonResponse({"error": "Username doesn't exists!"}, status=404)
    
    if user1 == user2:
        return JsonResponse({"error": "User cannot follow itself!"}, status=400)
    
    if user1.following.filter(username=username).exists():
        return JsonResponse({"error": f"User {user1.username} already follows user {user2.username}!"}, status=409)

    # Only now user1 can follow user2
    user1.following.add(user2)
    
    return JsonResponse({"message": f"User {user1.username} starts to follow user {user2.username}!"}, status=200)
    
    
# user1 is unfollowing user2
@login_required  
@csrf_exempt
def unfollow(request, username):
    user1 = request.user
    
    try:
        user2 = User.objects.get(username=username)
    except:
        return JsonResponse({"error": "Username doesn't exists!"}, status=404)
    
    if user1 == user2:
        return JsonResponse({"error": "User cannot unfollow itself!"}, status=400)
    
    if user1.following.filter(username=username).exists():
        # Only now user1 can unfollow user2
        user1.following.remove(user2)
        return JsonResponse({"message": f"User {user1.username} unfollows user {user2.username}!"}, status=200)
    else:
        return JsonResponse({"error": f"User {user1.username} didn't follow user {user2.username}!"}, status=404)

  
# Function for getting all posts from the following users      
@login_required
def following(request):
    following = User.objects.get(pk=request.user.id).following.all()
    followeers_posts = Post.objects.filter(user__in=following)
    
    # If user is logged in then we can search for all liked posts by user
    liked_posts_by_user = set()
    if request.user.is_authenticated:
        liked_posts_by_user = set(Like.objects.filter(user=request.user).values_list('post_id', flat=True))

    # Each post will have is_liked value True/False   
    for post in followeers_posts:
        post.is_liked = post.id in liked_posts_by_user

    p = Paginator(followeers_posts, POSTS_PER_PAGE)
    page_num = request.GET.get("page")
    page_obj = p.get_page(page_num)

    return render(request, "network/following.html", context={
        "page_obj": page_obj,
    })


# Function for liking the post. Only logged in user can like the post
@login_required
def like(request, post_id):
    
    try:
        post = Post.objects.get(pk=int(post_id))
    except:
        return JsonResponse({"error": f"Post with id = {post_id} doesn't exists!"}, status=404)
    
    Like.objects.create(user=request.user, post=post)
    
    return JsonResponse({"message": f"User {request.user.username} likes post from the user {post.user.username}!",
                         "post id": post_id,
                         "post content": post.content }, status=200)
        

# Function for liking the post. Only logged in user can like the post
@login_required
def unlike(request, post_id):
    
    try:
        post = Post.objects.get(pk=int(post_id))
    except:
        return JsonResponse({"error": f"Post with id = {post_id} doesn't exists!"}, status=404)
    
    like = Like.objects.filter(user=request.user, post=post)
    
    if like:
        like.delete()
        return JsonResponse({"message": f"User {request.user.username} unlikes post from the user {post.user.username}!",
                            "post id": post_id,
                            "post content": post.content }, status=200)
    else:
        return JsonResponse({"error": f"User {request.user.username} didn't like the post with id={post_id} from the user {post.user.username} exists!"}, status=404)