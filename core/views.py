import json
from django.db.models import BooleanField, Case, When, Value
from django.views.generic import ListView
from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse ,HttpResponse,HttpResponseForbidden
from django.contrib import messages 
from django.contrib.auth import update_session_auth_hash,logout,authenticate,login,get_user_model
from django.contrib.auth.decorators import login_required
from .models import StaffUser
from .forms import *
# Create your views here.
User = get_user_model()
def context_data(request):
    fullpath = request.get_full_path()
    abs_uri = request.build_absolute_uri()
    abs_uri = abs_uri.split(fullpath)[0]
    context = {
        'system_host': abs_uri,
        'page_name':'',
        'page_title':'',
        'system_name' : 'Accounts Managament System',
        'topbar':True,
        'footer':True,
    }
    return context

def login_page(request):
    context = context_data(request)
    context['topbar'] = False
    context['footer'] = False
    context['page_name'] = 'login'
    context['page_title'] = 'Login'
    return render(request,'core/login.html',context)

def logout_user(request):
    logout(request)
    return redirect("core:login-page")

def login_user(request):
    logout(request)
    resp = {
        "status":'failed',
        'msg':''
    }
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username = username,password=password)
        if user is not None:
            if user.is_active:
                login(request,user)
                resp['status'] = 'success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type = 'application/json')

@login_required
def users_list(request):
    context = context_data(request)
    context['page'] = 'users'
    context['page_title'] = 'Users'
    context['page_name'] = context['system_name']
    if (request.user.staffuser if hasattr(request.user, 'staffuser') else False) or request.user.is_superuser:
        context['staff_users'] = StaffUser.objects.all()
        if request.user.is_superuser:
            users = User.objects.exclude(id = request.user.id)
        else:
            users = User.objects.filter(assigned_staff__user = request.user)
    else:
        return redirect('accounts:user-detail')
        
    context['users'] = users
    return render(request,'core/user_list.html',context)

@login_required
def save_user(request):
    resp = {
        'status':'failed',
        'msg':''
    }
    
    if request.method == 'POST':
        post = request.POST
        user_id = post.get('id','')
        staff = post.get('staff','')
        is_staff = post.get('is_staff','')
        if user_id:
            user = get_object_or_404(User,id=user_id)
            if request.user.is_superuser or (request.user.staffuser if hasattr(request.user, 'staffuser') else False) and (user.assigned_staff.user if hasattr(user.assigned_staff, 'user') else None)==request.user:
                
                    form = UpdateUser(post,instance=user)
            else:
                resp['msg'] = "You are not authorized to edit Users"
                return JsonResponse(resp)
        else:
            if request.user.is_superuser or  (request.user.staffuser if hasattr(request.user, 'staffuser') else False):
                    form = SaveUser(post)
            else:
                resp['msg'] = "You are not authorized to Add Users"
                return JsonResponse(resp)

        if form.is_valid():
            save_instance = form.save(commit=False)
            try:
                assigned_staff = StaffUser.objects.get(user__username = staff)
            except:
                assigned_staff = None
            if request.user.is_superuser:
                if user_id:
                    if is_staff == 'on' and not staff:
                        staff_user,created = StaffUser.objects.get_or_create(user=user)
                        assigned_staff = None
                        
                    else:
                        StaffUser.objects.filter(user=user).delete()
                    messages.success(request, "User has been updated successfully.")
                else:
                    if assigned_staff and not is_staff:
                        assigned_staff = assigned_staff
                    elif not is_staff:
                        assigned_staff = None
                    else:
                        save_instance.save()
                        staffuser , _ = StaffUser.objects.get_or_create(user=save_instance)
                        resp['status']  = 'success'
                        return JsonResponse(resp)

            else:
                staff_instance = get_object_or_404(StaffUser,user=request.user)
                assigned_staff = staff_instance

                
            save_instance.assigned_staff = assigned_staff
            save_instance.save()
            resp['status']  = 'success'
        else:
            for field in form:
                for error in field.errors:
                    resp['msg'] += f"[{field.name}] {error} <br/>"
    
    else:
        resp['msg'] = "There's no data sent on the request"

    return JsonResponse(resp)

@login_required
def manage_user(request,pk=None):
    context = context_data(request)
    context['page'] = 'manage_user'
    context['page_title'] = 'Manage User'
    if pk is None:
        if request.user.is_superuser or  (request.user.staffuser if hasattr(request.user, 'staffuser') else False):
            context['user'] = {}
            if request.user.is_superuser:
                context['staff_users'] = StaffUser.objects.only('user')
        else:
            return HttpResponse("You are not authorized to add Users")
        
    else:
        
        if request.user.is_superuser or request.user.has_perm('core.change_user') and (request.user.staffuser if hasattr(request.user, 'staffuser') else False):
            user = get_object_or_404(User,pk=pk)
            if (user.assigned_staff.user if hasattr(user.assigned_staff, 'user') else None)==request.user or request.user.is_superuser:
                if request.user.has_perm('core.can_assign_staff_user'):
                    staff_users = StaffUser.objects.all()
                    context['staff_users'] = staff_users
                    
                    if  (user.staffuser if hasattr(user, 'staffuser') else False):
                        context['is_staff'] = True
                    else:
                        context['is_staff'] = False
                context['user'] = user
            else:
                return HttpResponseForbidden()
        else:
            return HttpResponseForbidden()
        
    return render(request, 'core/manage_user.html', context)

@login_required
def delete_user(request, pk=None):
    resp = {
        'status': 'failed',
        'msg': ''
    }

    if pk:
        if request.user.is_superuser or (request.user.staffuser if hasattr(request.user, 'staffuser') else False):
            user = get_object_or_404(User,pk=pk)
            if user.is_active:
                try:
                    user.is_active = False
                    user.save()
                    messages.success(request, "User has been deactivated successfully")
                    resp['status'] = 'success'
                except Exception:
                    resp['msg'] = 'Deactivatibg User Failed'
                    
            else:
                try:
                    user.delete()
                    messages.success(request,"User has been deleted successfully")
                    resp['status'] = "success"
                except Exception:
                    resp['msg'] = 'Deleting User Failed'
        else:
            resp['msg'] = "You are not authorized to delete Users"
        
        return HttpResponse(json.dumps(resp),content_type="application/json")
    
    else:
        resp['msg'] = "There's no data sent in the request"

    return JsonResponse(resp)


