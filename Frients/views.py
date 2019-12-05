import threading
from datetime import time
from django.contrib.gis.geoip2 import GeoIP2
from django.db.models import Q
from django.shortcuts import render, render_to_response, redirect
from django import forms

from django.views.decorators.csrf import csrf_exempt
from .models import User, communicate
from django.contrib.gis.geos import Point, GEOSGeometry
from django.http import HttpRequest


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@csrf_exempt
def login(request):
    if request.method == "POST":

        uf = UserFormLogin(request.POST)
        if uf.is_valid():
            # 获取表单信息
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            userResult = User.objects.filter(username=username, password=password)
            # all = User.objects.all()
            # pdb.set_trace()
            if len(userResult) > 0:
                if 'delete' in request.POST:
                    userResult.delete()
                    return render_to_response('userlogin.html', {'dele': "This user has been delete"})
                request.session['user'] = username
                # return  render_to_response('success.html',{'data' : userResult, 'all':all})
                return redirect('mappage')
            else:
                return render_to_response('userlogin.html', {'fail': "This user not exist, Please try again"})
    else:
        uf = UserFormLogin()
    return render_to_response("userlogin.html", {'uf': uf})


@csrf_exempt
def register(request):

    if request.method == "POST":

        uf = UserForm(request.POST)
        if uf.is_valid():
            Latitude = uf.cleaned_data['latitude']
            Longitude = uf.cleaned_data['longitude']
            location = GEOSGeometry('POINT(%s %s)' % (Longitude, Latitude))
            username = uf.cleaned_data['username']
            filterResult = User.objects.filter(username=username)
            if len(filterResult) > 0:
                return render_to_response('register.html', {"errors": 'the user already exists'})
            else:
                password1 = uf.cleaned_data['password1']
                password2 = uf.cleaned_data['password2']
                errors = []
                if (password2 != password1):
                    errors.append("Please enter right password")
                    return render_to_response('register.html', {'errors': 'The two password is different'})
                password = password2
                user = User.objects.create(username=username, password=password1, location=location)
                user.save()
                return render_to_response('register.html', {'succ': "register successful"})
    else:
        uf = UserForm()

    return render_to_response('register.html', {'uf': uf})


@csrf_exempt
def map(request):
    #check login
    user = request.session.get('user')
    userResult = User.objects.filter(username=user).values('location')
    all = User.objects.all()
    # user2 = request.POST.get('toolsname')
    if user is None:
        render_to_response('success.html', {'miss': 'Please Login First'})
    else:
        if request.method == "POST":
            suc = mapform(request.POST)
            if 'trans' in request.POST:
                request.session['user2'] = request.POST['user2']
                return redirect('chat')
            if 'submit' in request.POST:
                if suc.is_valid():
                    descri = suc.cleaned_data['des']
                    obj = User.objects.get(username=user)
                    obj.describe = descri
                    obj.save()
                    return redirect('mappage')

        else:
            suc = mapform()
        return render_to_response('success.html', {'map': suc, 'data': userResult, 'all': all,'user':user})


@csrf_exempt
def chat(request):
    user2 = request.session.get('user2')
    user1 = request.session.get('user')
    userResult = communicate.objects.filter(Q(username1=user1, username2 = user2)|Q(username1=user2, username2 = user1))
    if user1 is None:
        render_to_response('chat.html', {'miss': 'Please Login First'})
    else:
        if request.method == "POST":
            chatf = chatform(request.POST)
            if chatf.is_valid():
                chat = user1 + ": " + chatf.cleaned_data['chat']
                user = communicate.objects.create(username1=user1, username2=user2, text=chat)
                user.save()
                return redirect('chat')
        else:
            chatf = chatform()

        return render_to_response('chat.html', {'data': userResult, 'chatf': chatf, 'user1':user1, 'user2':user2})



class UserForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Password Confirm', widget=forms.PasswordInput())
    latitude = forms.CharField(label='Latitude', max_length=100, widget=forms.TextInput(attrs={'id': 'Latitude'}))
    longitude = forms.CharField(label='Longitude', max_length=100, widget=forms.TextInput(attrs={'id': 'Longitude'}))


class UserFormLogin(forms.Form):
    username = forms.CharField( label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput())


class mapform(forms.Form):
    des = forms.CharField(label='Description', max_length=1000, widget=forms.Textarea(attrs={'id': 'desc','rows':2, 'cols':40}),
                          required=False)
    user2 = forms.CharField(label='User2', max_length=50, widget=forms.HiddenInput(), required=False)

class chatform(forms.Form):
    chat = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={'id': 'chat', 'rows':2, 'cols':40}),
                          required=False)