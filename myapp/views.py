from datetime import datetime, timedelta
from django.forms import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import never_cache
from .validate_userdetails import Validate_data
from ast import literal_eval 
import threading, json
from .send_email import *
from django.db.models import Count
# Create your views here.

global informations

def landing_page(request):
    return  render(request, 'landing_page.html')

def home(request):
    if not request.user.is_authenticated:
        return redirect("user_login")
    
    result = {}

    try:
        categorys = MovieCategory.objects.all()

        for cat in categorys:
            movies = Movies.objects.filter(category_name=cat.id)
            
            result[cat.category_name] = movies
        print(result)    
        new_movies = Movies.objects.all().order_by('-created_at1')[0:5]
        context={'movies':result, 'new_movies': new_movies}
        # return render(request, 'added_movies.html')
        return  render(request, 'home.html',context)

    except MovieCategory.DoesNotExist:
        raise Exception("Movie category does not exist")
    
@never_cache
def user_signup(request):

    global informations 

    details_cookie = request.COOKIES.get('details', None)
    if details_cookie and literal_eval(details_cookie):
        return render(request, 'otp.html')
    
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == 'POST':

        password_1 = request.POST.get('password_1')
        password_2 = request.POST.get('password_2')
        
        
        if password_1 == password_2:

            
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')

            username = first_name + ' ' + last_name

            if User.objects.filter(email=email).exists():
                messages.error(request,'Email already exists!')

            if User.objects.filter(username=username).exists():
                messages.error(request,'username already exists!')    

            else:

                output_dict = Validate_data(email=email, password=password_2).validate_all()

                if not output_dict['all_correct']:
                    output_dict.pop('all_correct')
                    print("message sented")
                    messages.error(request, output_dict)
                    return redirect('user_signup')
                
                informations = {
                    'username':username,
                    'password':password_2,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email':email
                }
                res = render(request, 'otp.html')
                expiration_time = datetime.now() + timedelta(seconds=30)

                # Set the cookie with expiration time
                res.set_cookie('details', informations, expires=expiration_time)
                # send_otp(request, email, username)
                thread = threading.Thread(target=send_otp, args=(request, email, username)) 
                thread.start() 

                messages.success(request, "Sucessfully registered")
                return res
            
        messages.error(request, "Both Password Not Matching.....!!!")
        return redirect('user_signup')    

    return render(request, 'signup.html')


def user_login(request):


    if request.user.is_authenticated:
        return redirect("/")
    
    global informations

    if request.method == 'POST':

        password_1 = request.POST.get('password_1')
        password_2 = request.POST.get('password_2')
        
        
        if password_1 == password_2:
            
            email = request.POST.get('email')
            username = request.POST.get('username')

            if not User.objects.filter(email=email).exists():
                messages.error(request,"Email doesn't exists!")
                return redirect('user_login')
            
            output_dict = Validate_data(email=email, password=password_2).validate_all()

            print(output_dict)
            if not output_dict['all_correct']:
                output_dict.pop('all_correct')
                messages.error(request, output_dict)
                return redirect('user_login')
            
            user = authenticate(username=username, password=password_2)
            if user is None:
                messages.error(request,"Invalid Email or Password......!!!\nPlease try again.")
                return redirect('user_login')
            
            if user.is_active:
                login(request,user)
                return redirect('/')  

            messages.error(request, "Your Accout is Blocked")
            return redirect('user_login')    

        messages.error(request, "Both Password Not Matching.....!!!")
        return redirect('user_login')    

    return render(request, 'login.html')


def verify_otp(request):
    
    global informations

    if request.method == "POST":
        
        otp1 = request.POST.get('otp1')
        otp2 = request.POST.get('otp2')
        otp3 = request.POST.get('otp3')
        otp4 = request.POST.get('otp4')
        otp5 = request.POST.get('otp5')
        otp6 = request.POST.get('otp6')

        list=[otp1,otp2,otp3,otp4, otp5, otp6]

        string_num =[str(i) for i in list]
        int_otp = int("".join(string_num))

        try:

            curr_otp = OTP_COLLECTION_db.objects.get(otp=int_otp)
            # Get the current time in UTC timezone
            now = timezone.now()

            # Set the expiry time with timezone information
            expiry_time = now + timedelta(minutes=1)

            # Check if the expiry time has passed
            if now > curr_otp.expireTime:
                messages.error(request, "This OTP has already expired")
                return render(request, 'otp.html')
            else:
                us_obj = User.objects.create_user(username=informations['username'], password=informations['password'], last_name = informations['last_name'], first_name = informations['first_name'], email = informations['email'])
                print('user created')
                login(request, us_obj)
                curr_otp.delete()
                return redirect('/')
            
        except OTP_COLLECTION_db.DoesNotExist:
            messages.error(request, "INVALID OTP TRY AGAIN...!!!") 
            return render(request, 'otp.html')   

def resent_otp(request):
    global informations
    otp_data = get_object_or_404(OTP_COLLECTION_db, informations['email'])
    if otp_data.No_of_times  >= 3 :
        messages.error(request, "Your Otp limit reached...!!!")
        return render(request, 'otp.html')
    else:
        thread = threading.Thread(target=send_otp, args=(request, informations['email'], informations['username'])) 
        thread.start() 
        messages.success(request, "OTP Resent successfully..")
        return render(request, 'otp.html')

def sent_otps(request):
    if request.user.is_authenticated:
        thread = threading.Thread(target=send_otp, args=(request, request.user.email, request.user.username)) 
        thread.start() 
        messages.success(request, "Sucessfully registered")
        return render(request, 'otp.html')
    return redirect('user_login')
    

def user_logout(request):
    logout(request)
    return redirect('user_login')

def profile_page(request):
    if not request.user.is_authenticated:
        return redirect('user_login')
    curr_user = request.user
    if request.method == 'POST':

        new_username = request.POST.get("username")
        new_email = request.POST.get("email")
        try:
            user_data = User.objects.get(id=curr_user.id)
            user_data.username = new_username
            user_data.email = new_email
            user_data.save()
            messages.success(request, "Sucessfully Updated")
            return redirect('profile_page')
        except:
            messages.error(request, "Something went wrong!! Please Try Again.")
            return redirect('profile_page')
    
    
    return render(request, 'profile.html', {'user_data': curr_user})


def add_category(request):

    if not request.user.is_authenticated:
        return redirect("user_login")

    added_category = MovieCategory.objects.all()

    if request.method == 'POST':
        category_name = request.POST.get('Category_name')
        category_describtion = request.POST.get('Category_text', None)
        
        print(category_name, category_describtion)

        if not category_name:
            messages.error(request, 'Please enter a Category Name!')
            return redirect('add_category')
        
        MovieCategory(category_name=category_name,describtion=category_describtion).save()

        messages.success(request, "category add successfully..!!!")
        return redirect('add_category')
    
       
    return render(request, 'category.html', {'category': added_category})

def add_movies(request):

    categorys = MovieCategory.objects.all()

    if request.method=='POST':
        movie_poster = request.FILES.get('poster')
        title = request.POST.get('title')
        date = request.POST.get('created')
        link = request.POST.get('youtube_link')
        actors = request.POST.get('actors')
        discribtion = request.POST.get('describtion')
        category = request.POST.get('selected')

        # print(movie_poster, title, date, link, actors, discribtion, category)

        if not all([movie_poster, title, date, link, actors, discribtion, category]):
            messages.error(request, "All fields are required...!!!")
            return redirect('add_movies')

        splited_data = actors.split(',')
        actors_dict = {}

        for indx , actors in enumerate(splited_data):
            actors_dict[f"actor{indx}"]=actors

        new_movie = Movies()
        new_movie.user = request.user
        new_movie.movie_title = title
        new_movie.describtion = discribtion
        new_movie.image = movie_poster
        new_movie.release_date = date
        new_movie.actors = json.dumps(actors_dict)
        new_movie.youtube_link = link
        new_movie.category_name = MovieCategory.objects.get(category_name=category)
        new_movie.save()

        messages.success(request, "New Movie add Sucessfully...!!!")
        return redirect('add_movies')

    return render(request, 'add_movies.html', {'category': categorys})


def edit_movies(request, id):
    print(id)
    movies = get_object_or_404(Movies, pk=id)
    
    if request.method=='POST':

        
        if request.FILES.get('poster'):
            movie_poster = request.FILES.get('new')
        else:
            movie_poster = request.POST.get('poster')
        title = request.POST.get('title')
        date = request.POST.get('created')
        link = request.POST.get('youtube_link')
        actors = request.POST.get('actors')
        discribtion = request.POST.get('describtion')
        category = request.POST.get('selected')

        print(movie_poster, title, date, link, actors, discribtion, category)

        if not all([movie_poster, title, date, link, actors, discribtion, category]):
            messages.error(request, "All fields are required...!!!")
            return redirect('added_movies')
        
        actors_dict = json.loads(actors)
        new_movie = Movies.objects.get(id=id)
        new_movie.user = request.user
        new_movie.movie_title = title
        new_movie.describtion = discribtion
        new_movie.image = movie_poster
        new_movie.release_date = date
        new_movie.actors = json.dumps(actors_dict)
        new_movie.youtube_link = link
        new_movie.category_name = MovieCategory.objects.get(category_name=category)
        new_movie.save()
        
        messages.success(request, "Movie updated Sucessfully...!!!")
        return redirect('added_movies')
    
    return render(request, 'edit_movie.html', {"movie": movies})


def delete_movies(request, id):
        Movies.objects.get(id=id).delete()
        messages.error(request, "Movie deleted Sucessfully...!!!")
        return redirect('added_movies')

def added_movies(request):

    result = {}

    try:
        categorys = MovieCategory.objects.all()

        for cat in categorys:
            movies = Movies.objects.filter(category_name=cat.id, user=request.user)
            
            result[cat.category_name] = movies
        print(result)    
        context={'movies':result}
        return render(request, 'added_movies.html',context)
    except MovieCategory.DoesNotExist:
        raise Exception("Movie category does not exist")


def search_movies(request):
    query = request.GET.get('item')

    data = Movies.objects.filter(movie_title__icontains=query).select_related('category_name')

    print(data, "hcscscnscnsc")
    return render(request, 'search_result.html', {'result': data})


def add_comment(request, movie_id, user_id):
    if request.method == 'POST':
        movie = get_object_or_404(Movies, id=movie_id)
        user = get_object_or_404(User, id=user_id)
        comments = request.POST.get('text')
        comment = MovieComment(movie=movie, user_name=user, text=comments)
        comment.save()
        messages.success(request, "review added Sucessfully...!!!")
        return redirect('reviews', id=movie_id)

def add_likes(request,movie_id, user_id):
    
    movie = get_object_or_404(Movies, id=movie_id)
    user = get_object_or_404(User, id=user_id)
    comment = MovieComment(movie=movie, user_name=user)
    comment.save()
    comment.likers.set([request.user])
    return redirect('reviews', id=movie_id)

def view_movie_reviews(request, id):
    movie_obj = get_object_or_404(Movies, id=id)
    likers_count = MovieComment.objects.filter(movie=movie_obj).aggregate(Count('likers'))['likers__count']
    comments_count = MovieComment.objects.filter(movie=movie_obj).aggregate(Count('text'))['text__count']
    all_comments = MovieComment.objects.filter(movie=movie_obj)
    return render(request,'movie_reviews.html',{'movie':movie_obj, 'likers_count': likers_count, 'comments_count':comments_count, 'all_comments': all_comments})


