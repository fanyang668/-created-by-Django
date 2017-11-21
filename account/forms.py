# -*- coding:utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, UserInfo


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = ('school', 'company', 'profession', 'address', 'aboutme', 'photo')


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('birth', 'phone')


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        # 申明数据写入的模型类，以及写入的字段
        model = User
        fields = ('username', 'email')

    def clean_password2(self):
        # 凡是'clean_'+'自定义'的函数都会和此表单实例化对象的is_valid()方法同时执行
        cd = self.cleaned_data
        # 判断两次输入的密码是否一致
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("password do not match.")
        return cd['password2']


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

