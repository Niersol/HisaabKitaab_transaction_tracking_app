import json
from django.db import transaction
from django.db.models import Max
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.db.models import BooleanField, Case, When, Value
from django.views.generic import ListView
from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse ,HttpResponse,HttpResponseForbidden
from django.contrib import messages 
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import update_session_auth_hash,logout,authenticate,login,get_user_model
from django.contrib.auth.decorators import login_required
from .models import *
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

@login_required
def user_detail(request, pk=None):
    context = context_data(request)
    context['page'] = 'parties'
    context['page_title'] = 'Parties'
    options = []

    if pk:
        try:
            user = User.objects.get(pk=pk)
            if (user.assigned_staff.user if hasattr(user.assigned_staff, 'user') else None)==request.user or request.user.is_superuser:
                context['parties'] = Party.objects.select_related('user').filter(user = user)
                context['page_name'] = user
                context['user'] = user
                options.append(('manage_transactions','Manage Transactions')) 
                options.append(('manage_s_p','Manage Sale/purchases')) 
            else:
                return HttpResponse(status=204)
        except User.DoesNotExist:
            return HttpResponse(status=204)
    else:
        if (request.user.staffuser if hasattr(request.user, 'staffuser') else False) or request.user.is_superuser:
                return HttpResponse(status=204)
        context['parties'] = Party.objects.filter(user = request.user)
        context['page_name'] = request.user
        context['user'] = request.user
        options.append(('manage_transactions','Manage Transactions')) if request.user.has_perm('accounts.can_manage_transactions') else None
        options.append(('manage_s/p','Manage Sale/purchases')) if request.user.has_perm('accounts.can_manage_s/p') else None
    context['options'] = options
    return render(request,'accounts/party.html',context)

@login_required
def manage_party(request,pk=None):
    context = context_data(request)
    context['page'] = 'manage_user'
    context['page_title'] = 'Manage User'

    if pk :
        party = Party.objects.select_related('user').get(pk=pk)
        if party:
            if request.user.is_superuser or (request.user.staffuser if hasattr(request.user, 'staffuser') else False) and (party.user.assigned_staff.user if hasattr(party.user.assigned_staff, 'user') else None)==request.user or request.user == party.user and request.user.has_perm('accounts.change_party'):
                    context['party'] = party
            else:
                HttpResponse("You are not Authorized to Edit This Party")
        else:
            return HttpResponse("The party is invalid")        
          
    else:
        if request.user.is_superuser or (request.user.staffuser if hasattr(request.user, 'staffuser') else False) and (request.user.assigned_staff.user if hasattr(request.user.assigned_staff, 'user') else None)==request.user or  request.user.has_perm('accounts.add_party'):
            context['user_id'] = request.GET.get('user_id')
        else:
            HttpResponse("You are not Authorized to Add This Party")
    return render(request, 'accounts/manage_party.html', context)
            
@login_required
def save_party(request):
    resp = {'status': 'failed', 'msg': ''}

    if request.method == 'POST':
        post = request.POST
        party_id = post.get('id','')
        user_id = post.get('user','')
        if user_id:
            user = User.objects.get(pk=user_id)
            if party_id:
                party = Party.objects.select_related('user').get(pk=party_id)
                if request.user.is_superuser or party.user == request.user and request.user.has_perm('accounts.change_party') or (request.user.staffuser if hasattr(request.user, 'staffuser') else False) and (party.user.assigned_staff.user if hasattr(party.user.assigned_staff, 'user') else None)==request.user:
                    form = SaveParty(post, instance=party)
                else:
                    resp['msg'] = "You are not authorized to edit Party"
                    return JsonResponse(resp)
            else:
                if request.user.is_superuser or user == request.user and request.user.has_perm('accounts.add_party') or (request.user.staffuser if hasattr(request.user, 'staffuser') else False) and (user.assigned_staff.user if hasattr(user.assigned_staff, 'user') else None)==request.user:
                    form = SaveParty(post)
                else:
                    resp['msg'] = "You are not authorized to Add Party"
                    return JsonResponse(resp)
                
        if form.is_valid():
            form.save()

            if party_id == '':
                messages.success(request, "Party has been saved successfully.")
            else:
                messages.success(request, "Party has been updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if resp['msg'] != '':
                        resp['msg'] += '<br/>'
                    resp['msg'] += f'[{field.name}] {error}'

    else:
        resp['msg'] = "There's no data sent in the request"
    return JsonResponse(resp)


@login_required
def delete_party(request, pk=None):
    resp = {
        'status': 'failed',
        'msg': ''
    }

    if pk:
        party = Party.objects.select_related('user').filter(pk = pk)
        if party:
            if request.user.is_superuser or party.user == request.user and request.user.has_perm('accounts.add_party') or (request.user.staffuser if hasattr(request.user, 'staffuser') else False) and (party.user.assigned_staff.user if hasattr(party.user.assigned_staff, 'user') else None)==request.user:            
                if party.delete_flag == 0:
                    try:
                        party.update(delete_flag=1)
                        messages.success(request, "Party has been moved to recycle bin successfully.")
                        resp['status'] = 'success'
                    except:
                        resp['msg'] = "Deleting User Failed."
                else:
                    party.delete()
                    messages.success(request,"Party has been deleted successfully.")
                    resp['status'] = 'success'
            else:
                return HttpResponse(status=204)
        else:
            return HttpResponse(status=204)
    
    else:
        resp['msg'] = "There's no data sent in the request"

    return HttpResponse(json.dumps(resp),content_type="application/json")

@login_required
def manage_transaction(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_transaction'
    context['page_title'] = 'Manage Transaction'
    
    user_id = request.GET.get('user_id', '')
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return HttpResponse(status=204)

    if pk is None:
        # Adding a new transaction
        if (request.user.is_superuser or 
            (user == request.user and request.user.has_perm('accounts.add_transaction')) or
            (hasattr(request.user, 'staffuser') and request.user.staffuser and
             user.assigned_staff.user == request.user)):
            
            context['user_id'] = user.id
            context['parties'] = Party.objects.filter(user=user, delete_flag=0)
        else:
            return HttpResponse("You are not allowed to manage Transactions. Please contact admin for further queries")
    else:
        # Editing an existing transaction
        if (request.user.is_superuser or 
            (user == request.user and request.user.has_perm('accounts.change_transaction')) or
            (hasattr(request.user, 'staffuser') and request.user.staffuser and
             user.assigned_staff.user == request.user)):
            transaction = get_object_or_404(Transaction, pk=pk)
            context['user_id'] = user.id
            transaction_data =      {'party': transaction.party.name,
                                    'description': transaction.description,
                                    'user': transaction.party.user.username,
                                    'debit': transaction.debit,
                                    'credit': transaction.credit,
                                    'date': transaction.form.created_at,
                                    'id':transaction.pk}
            
            return JsonResponse({'transaction':transaction_data})
        else:
            return HttpResponse("You are not allowed to manage Transactions. Please contact admin for further queries")

    return render(request, 'accounts/manage_transaction.html', context)

@login_required
def save_transaction(request):
    resp = {'status': 'failed', 'msg': '', 'transaction': None}

    if request.method == 'POST':

        post = request.POST
        id = post.get('id','') 
        user_id = post.get('user_id','') 
        date = post.get('date', '')
        party = post.get('name', '')
        debit = post.get('debit','')
        credit = post.get('credit','')
        if user_id:
            party = Party.objects.get(name=party,user__id=user_id)
            if party:
                form_obj, created = Form.objects.get_or_create(created_at=date)
                if id:
                    transaction = Transaction.objects.get(id = id)
                    if request.user.is_superuser or party.user == request.user and request.user.has_perm('accounts.change_transaction') or (request.user.staffuser if hasattr(request.user, 'staffuser') else False) and (party.user.assigned_staff.user if hasattr(party.user.assigned_staff, 'user') else None)==request.user:
                        form = SaveForm(post,instance=transaction)
                    else:
                        resp['msg'] = "You are not authorized to Edit Transaction "
                        return JsonResponse(resp)
                else:
                    if request.user.is_superuser or party.user == request.user and request.user.has_perm('accounts.add_transaction') or (request.user.staffuser if hasattr(request.user, 'staffuser') else False) and (party.user.assigned_staff.user if hasattr(party.user.assigned_staff, 'user') else None)==request.user:
                        form = SaveForm(post)
                    else:
                        resp['msg'] = "You are not authorized to Add transaction"
                        return JsonResponse(resp)
            else:
                return JsonResponse(status=204)

            if form.is_valid():
                transaction_instance = form.save(commit=False)
                transaction_instance.party = party
                transaction_instance.form = form_obj
                if debit == '':
                    transaction_instance.debit = 0
                if credit == '':
                    transaction_instance.credit = 0
                transaction_instance.save()
                resp['status'] = 'success'
            
            else:
                for field in form:
                    for error in field.errors:
                        if resp['msg'] != '':
                            resp['msg'] += '<br/>'
                        resp['msg'] += f'[{field.name}] {error}'
    else:
        resp['msg'] = "There's no data sent in the request"

    return JsonResponse(resp)

@login_required
def transaction_list(request):
    if request.method == 'GET':
        selected_date = request.GET.get('date')
        user_id = request.GET.get('user_id')
        user = User.objects.get(pk=user_id)
        if user:
            if request.user.is_superuser or user == request.user and request.user.has_perm('accounts.add_transaction') or (request.user.staffuser if hasattr(request.user, 'staffuser') else False) and (user.assigned_staff.user if hasattr(user.assigned_staff, 'user') else None)==request.user:
                if selected_date == '2000-01-01':
                    transactions = Transaction.objects.select_related('party__user').filter(delete_flag=0,party__delete_flag=0,party__user = user)
                else:
                    transactions = Transaction.objects.select_related('party__user').filter(delete_flag=0,party__delete_flag=0,form__created_at=selected_date,party__user = user)
                transaction_data = [{'party': transaction.party.name,
                                    'description': transaction.description,
                                    'user': transaction.party.user.username,
                                    'debit': transaction.debit,
                                    'credit': transaction.credit,
                                    'date': transaction.form.created_at,
                                    'id':transaction.pk} for transaction in transactions]

                return JsonResponse({'transactions': transaction_data})
        
            else:
                return JsonResponse({
                    "msg" : "You are not authorized to view transaction"
            })
        else:
            JsonResponse(status=204)
 
@login_required
def delete_transaction(request,pk=None):
    resp = {
        'status':'failed',
        'msg':''
    } 
    
    if pk:  
        transaction = models.Transaction.objects.select_related('party__user').filter(pk = pk)
        if transaction:
            if request.user.is_superuser or transaction[0].party.user == request.user and request.user.has_perm('accounts.delete_transaction') or (request.user.staffuser if hasattr(request.user, 'staffuser') else False) and (transaction[0].party.user.assigned_staff.user if hasattr(transaction[0].party.user.assigned_staff, 'user') else None)==request.user:   
                if transaction[0].delete_flag == 0:
                    try:
                        transaction.update(delete_flag =1)
                    except:
                        resp['msg'] = "Deleting Transaction Failed."
                else:
                    try:
                        transaction.delete()
                        messages.success(request,"Transaction hasd been deleted successfully") 
                        resp['status'] = "success"
                    except:
                        resp['msg'] = 'Deleting user failed'
            else:  
                resp['msg']= "you are not authorized to delete transactions"
                return HttpResponse(json.dumps(resp))
        else:

            resp['msg']= "No transaction found with the given id"
            return HttpResponse(status=204)
        
    else:
        resp['msg'] = "You are not authorized to delete Transaction"
    return HttpResponse(json.dumps(resp),content_type = "application/json")

@login_required
def view_transactions(request,pk=None):
    if request.method == 'GET':
        party = models.Party.objects.get(id=pk)
        if party.user == request.user and request.user.has_perm('accounts.view_transaction') or request.user.is_superuser or (request.user.staffuser if hasattr(request.user, 'staffuser') else False) and (party.user.assigned_staff.user if hasattr(party.user.assigned_staff, 'user') else None)==request.user:
            transactions = models.Transaction.objects.select_related('party').filter(delete_flag=0,party = party).order_by('form__created_at', 'time')
            return render(request, 'accounts/transactions.html', {'transactions': transactions,"party":party})
        else:
            return HttpResponse(status=204)
        
    else:
        return HttpResponse(status=403)
   

@login_required
def manage_sales_purchases(request,pk=None):
    context = context_data(request)
    context['page'] = 'manage_sales_purchases'
    context['page_title'] = 'Manage Sales/Purchases'

        
    user_id = request.GET.get('user_id', '')
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return HttpResponse(status=204)
    
    if pk is None:
        if (request.user.is_superuser or 
            (user == request.user and request.user.has_perm('accounts.add_transaction')) or
            (hasattr(request.user, 'staffuser') and request.user.staffuser and
             user.assigned_staff.user == request.user)):
            
            context['user_id'] = user.id
            context['parties'] = Party.objects.filter(user=user, delete_flag=0)
            context['products'] = Product.objects.filter(user=user,delete_flag=0)
        else:
            return HttpResponse("You are not allowed to manage Transactions. Please contact admin for further queries")

    else:
        if (request.user.is_superuser or 
            (user == request.user and request.user.has_perm('accounts.change_transaction')) or
            (hasattr(request.user, 'staffuser') and request.user.staffuser and
            user.assigned_staff.user == request.user)):
            try:
                transaction = Trade.objects.get(pk=pk)
            except Trade.DoesNotExist:
                return JsonResponse({'status': 'failed', 'msg': 'Transaction is invalid'})
            transaction_items = TradeItem.objects.filter(trade=transaction)
            transaction_items_list = [
                {
                    'productName': item.product.name,
                    'quantity': item.quantity,
                    'price': item.price,
                    'total': item.quantity *  item.price,

                } for item in transaction_items
            ]
            context['user_id'] = user.id
            transaction_data = {
                'bill_number':transaction.bill_number,
                'party': transaction.party.name,
                'description': transaction.description,
                'debit': transaction.debit,
                'credit': transaction.credit,
                'date': transaction.form.created_at,
                'discount':transaction.discount,
                'id': transaction.pk,
                'items': transaction_items_list
            }

            return JsonResponse({
                'status': 'success',
                'msg': '',
                'transaction': transaction_data
            })
        else:
            return HttpResponse("You are not allowed to manage Transactions. Please contact admin for further queries")

    return render(request, 'accounts/manage_sales_purchase.html', context)


@login_required
def save_trade(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':

        data = json.loads(request.body)
        id = data.get('id','')
        user_id = data.get('user_id','')
        bill = data.get('bill_number',0) 
        name = data.get('name','') 
        date = data.get('date','')
        description = data.get('description','')
        state = data.get('state','off')
        total = data.get('total',0)
        discount = data.get('discount',0)
        items = data.get('items','')
        if discount == None:
            discount = 0
        if date:
            try:
                form_obj, created = Form.objects.get_or_create(created_at=date)
            except Exception:
                resp['msg'] = "Date is invalid"
                return JsonResponse(resp)
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                products = Product.objects.filter(user=user)
            except Exception:
                resp['msg'] = "User isn't valid"
                return JsonResponse(resp)

            try:
                party = Party.objects.get(name=name,user__id=user_id)
            except Exception:
                resp['msg'] = "Party couldn't be found"
                return JsonResponse(resp)
        else:
            resp['msg'] = "Couldn't find any reference to user"
            return JsonResponse(resp)
        
           

        if id:
            try:
                trade = Trade.objects.filter(id=id)
                transaction = Transaction.objects.filter(trade=trade)
            except Exception:
                resp['msg'] = "Couldn't find any transaction"
                return JsonResponse(resp)
            if state == "on" and request.user.is_superuser or party.user == request.user and request.user.has_perm('accounts.can_manage_sales') or (request.user.staffuser if hasattr(request.user, 'staffuser') else False) and (party.user.assigned_staff.user if hasattr(party.user.assigned_staff, 'user') else None)==request.user:
                try:
                    transaction.update(party=party,description=description,debit=total,form=form_obj)
                    trade.update(party=party,description=description,debit=total,form=form_obj,discount=discount,is_sales=True)
                    TradeItem.objects.filter(trade=trade[0]).delete()
                    trade_items = [
                        TradeItem(
                            trade=trade[0],
                            product=products.filter(name=item['productName'])[0],
                            quantity=item['quantity'],
                            price=item['price']
                        ) for item in items
                    ]
                    TradeItem.objects.bulk_create(trade_items)
                    resp['msg'] = "Updated Sale Successfully"
                except Exception:
                    resp['msg'] = "Couldn't Update Sale"
                    return JsonResponse(resp)
            elif state == 'off' and request.user.is_superuser or party.user == request.user and request.user.has_perm('accounts.can_manage_transaction') or (request.user.staffuser if hasattr(request.user, 'staffuser') else False) and (party.user.assigned_staff.user if hasattr(party.user.assigned_staff, 'user') else None)==request.user:
                try:
                    with transaction.atomic():
                        transaction.update(party=party,description=description,credit=total,form=form_obj)
                        trade.update(party=party,description=description,credit=total,form=form_obj,discount=discount,is_sales=False)
                        TradeItem.objects.filter(trade=trade[0]).delete()
                        trade_items = [
                            TradeItem(
                                trade=trade[0],
                                product=products.filter(name=item['productName'])[0],
                                quantity=item['quantity'],
                                price=item['price']
                            ) for item in items
                        ]
                        TradeItem.objects.bulk_create(trade_items)
                    resp['msg'] = "Updated Purchase Successfully"
                except Exception:
                    resp['msg'] = "Couldn't Update Purchase"
                    return JsonResponse(resp)
            else:
                resp['msg'] = "You don't have permission to upddate transactions"
                return JsonResponse(resp)

        else:
            if bill == None:
                bill = 0
                if state == 'on':
                    sales = Trade.objects.select_related('party__user').filter(delete_flag=0, party__delete_flag=0, party__user=user, is_sales=True)
                    bill = sales.aggregate(Max('bill_number'))['bill_number__max']
                    if bill:
                        bill = bill + 1
                    else:
                        bill =1
            if state == "on" and request.user.is_superuser or party.user == request.user and request.user.has_perm('accounts.can_manage_sales') or (request.user.staffuser if hasattr(request.user, 'staffuser') else False) and (party.user.assigned_staff.user if hasattr(party.user.assigned_staff, 'user') else None)==request.user:
                    with transaction.atomic():
                        trade = Trade.objects.create(
                            bill_number=bill,
                            party=party,
                            description=description,
                            debit=total,
                            form=form_obj,
                            discount=discount,
                            is_sales=True
                        )
                        trade_items = [
                            TradeItem(
                                trade=trade,
                                product=products.filter(name=item['productName'])[0],
                                quantity=item['quantity'],
                                price=item['price']
                            ) for item in items
                        ]
                        TradeItem.objects.bulk_create(trade_items)
                    
                    resp['msg'] = "Created new Sale successfully"
                
            elif state == "off" and request.user.is_superuser or party.user == request.user and request.user.has_perm('accounts.can_manage_purchase') or (request.user.staffuser if hasattr(request.user, 'staffuser') else False) and (party.user.assigned_staff.user if hasattr(party.user.assigned_staff, 'user') else None)==request.user:
                try:
                    with transaction .atomic():
                        trade = Trade.objects.create(bill_number=bill,party=party,description=description,credit=total,form=form_obj,discount=discount,is_sales=False)
                        trade_items = [
                            TradeItem(
                                trade=trade,
                                product=products.filter(name=item['productName'])[0],
                                quantity=item['quantity'],
                                price=item['price']
                            ) for item in items
                        ]
                        TradeItem.objects.bulk_create(trade_items)

                        resp['msg'] = "Created new Purchase Successfully"
                except Exception:
                    resp['msg'] = "Couldn't Create new Purchase"
                    return JsonResponse(resp)

            else:
                resp['msg'] = "You don't have permission to manage transactions"
                return JsonResponse(resp)
        resp['status'] = "success"
        return JsonResponse(resp)
    

@login_required
def sales_list(request):
    if request.method == 'GET':
        selected_date = request.GET.get('date')
        user_id = request.GET.get('user_id')
        user = User.objects.get(pk=user_id)
        if user:
            if request.user.is_superuser or user == request.user and request.user.has_perm('accounts.manage_sales') or (request.user.staffuser if hasattr(request.user, 'staffuser') else False) and (user.assigned_staff.user if hasattr(user.assigned_staff, 'user') else None)==request.user:
                if selected_date == '2000-01-01':
                    sales = Trade.objects.select_related('party__user').filter(delete_flag=0,party__delete_flag=0,party__user = user,is_sales=True)
                else:
                    sales = Trade.objects.select_related('party__user').filter(delete_flag=0,party__delete_flag=0,form__created_at=selected_date,party__user = user,is_sales=True)
                transaction_data = [{'party': transaction.party.name,
                                    'description': transaction.description,
                                    'debit': transaction.debit,
                                    'discount': transaction.discount,
                                    'date': transaction.form.created_at,
                                    'id':transaction.pk,
                                    'bill_number':transaction.bill_number} for transaction in sales]
                return JsonResponse({
                    'transactions': transaction_data,
                    })
        
            else:
                return JsonResponse({
                    "msg" : "You are not authorized to view transaction"
            })
        else:
            JsonResponse(status=204)

@login_required
def purchases_list(request):
    if request.method == 'GET':
        selected_date = request.GET.get('date')
        user_id = request.GET.get('user_id')
        user = User.objects.get(pk=user_id)
        if user:
            if request.user.is_superuser or user == request.user and request.user.has_perm('accounts.manage_purchase') or (request.user.staffuser if hasattr(request.user, 'staffuser') else False) and (user.assigned_staff.user if hasattr(user.assigned_staff, 'user') else None)==request.user:
                if selected_date == '2000-01-01':
                    purchase = Trade.objects.select_related('party__user').filter(delete_flag=0,party__delete_flag=0,party__user = user,is_sales=False)
                else:
                    purchase = Trade.objects.select_related('party__user').filter(delete_flag=0,party__delete_flag=0,form__created_at=selected_date,party__user = user,is_sales=False)
                transaction_data = [{'party': transaction.party.name,
                                    'description': transaction.description,
                                    'debit': transaction.credit,
                                    'discount': transaction.discount,
                                    'date': transaction.form.created_at,
                                    'id':transaction.pk,
                                    'bill_number':transaction.bill_number} for transaction in purchase]
                return JsonResponse({
                    'transactions': transaction_data,
                    })
        
            else:
                return JsonResponse({
                    "msg" : "You are not authorized to view transaction"
            })
        else:
            JsonResponse(status=204)