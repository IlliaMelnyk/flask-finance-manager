from flask import Blueprint, render_template, request, redirect, session, url_for, flash
import hashlib
from app.service.user_service import is_user, add_first_user


home=Blueprint('home',__name__, template_folder='templates')

@home.route('/')
def homepage():
   return render_template("homepage/homepage.html")

@home.route('/about')
def about():
    return render_template("homepage/about.html")

@home.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
   if request.method == 'POST':
       user=is_user(request.form)
       if user:
           session['user']=user
           return redirect("/auth/account")
       else:
           return render_template("homepage/sign_in.html", error="Bad credentials!")
   return render_template("homepage/sign_in.html")


@home.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        print(f"request.form = {request.form}")
        user=is_user(request.form)
        if not user:
            print("OK")
            add_first_user(request.form)
            return redirect("/sign_in")
        else:
            return render_template("homepage/sign_up.html", error="User with this parameters already exist!") 
    return render_template("homepage/sign_up.html")   
    