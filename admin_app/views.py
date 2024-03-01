from datetime import datetime, timedelta
from django.forms import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import never_cache
from myapp.validate_userdetails import Validate_data
from ast import literal_eval 
import threading, json
from myapp.send_email import *
from django.db.models import Count

# Create your views here.

def admin_login(request):

    if request.user.is_superuser:
        return redirect('/')
    
    if request.method == 'POST':

        password_1 = request.POST.get('password_1')
        password_2 = request.POST.get('password_2')
        
        
        if password_1 == password_2:
            
            email = request.POST.get('email')
            username = request.POST.get('username')

            if not User.objects.filter(email=email).exists():
                messages.error(request,"Email doesn't exists!")
                return redirect('admin_login')
            
            # output_dict = Validate_data(email=email, password=password_2).validate_all()

            # print(output_dict)
            # if not output_dict['all_correct']:
            #     output_dict.pop('all_correct')
            #     messages.error(request, output_dict)
            #     return redirect('admin_login')
            
            user = authenticate(username=username, password=password_2)
            if user is None:
                messages.error(request,"Invalid Email or Password......!!!\nPlease try again.")
                return redirect('admin_login')
            
            if user.is_superuser:
                login(request,user)
                return redirect('/')  

            messages.error(request, "Your not a super user")
            return redirect('admin_login')    

        messages.error(request, "Both Password Not Matching.....!!!")
        return redirect('admin_login')    

    return render(request, 'login.html')


def admin_home(request):

    if not request.user.is_superuser:
        return redirect('admin_login')

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
        return  render(request, 'admin_home.html',context)

    except MovieCategory.DoesNotExist:
        raise Exception("Movie category does not exist")

def  admin_logout(request):
    logout(request)
    return redirect("admin_login")

def view_and_block_user(request):
    
    if not request.user.is_superuser:
        return redirect('admin_login')

    
    if  request.method == "POST":
        user_id = request.POST.get('id')
        action_type = request.POST.get('action')
        print(user_id, action_type  )
        curr_user = User.objects.get(id=user_id)
        if action_type == 'block':
            curr_user.is_active = False
            curr_user.save()
            messages.success(request, 'user blocked..!!')
            return redirect('view_and_block_user')
        elif action_type == 'unblock':
            curr_user.is_active = True
            curr_user.save()

            messages.success(request, 'user unblocked..!!')
            return redirect('view_and_block_user')
        elif action_type == 'del':
            curr_user.delete()
            messages.error(request,'User deleted permanently...!')
            return redirect('view_and_block_user')

    return render(request, 'user_block.html', {'user_datas': User.objects.all()})

