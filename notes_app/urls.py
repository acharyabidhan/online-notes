from django.urls import path
from . import views

urlpatterns = [
    path('', views.render_home_page, name="render_home_page"),
    path('login', views.render_login_page, name="render_login_page"),
    path('signup', views.render_signup_page, name="render_signup_page"),
    path('account', views.render_account_page, name="render_account_page"),
    path('resetpassword/<str:uname>', views.reset_password, name="reset_password"),
    path('checkLogin', views.check_login, name="check_login"),
    path('checksignup', views.check_signup, name="check_signup"),
    path('savenotes', views.save_notes, name="save_notes"),
    path('deletenotes', views.delete_notes, name="delete_notes"),
]
