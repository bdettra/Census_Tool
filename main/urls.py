from django.urls import path
from . import views, admin, forms
from django.contrib.auth.views import LoginView, LogoutView
from datetime import datetime

urlpatterns=[
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('login/',
         LoginView.as_view
         (
             template_name='login.html',
             authentication_form=forms.AuthenticationForm,
             extra_context=
             {
                 'title': 'Log in',
                 'year' : datetime.now().year,
             }
         ),
         name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('admin/', admin.main_admin.urls,name='admin'),
    path('signup/',views.SignUpView.as_view(),name='signup'),
    path('dashboard/',views.client_dashboard,name='client_dashboard'),
    path('dashboard/create_client',views.createClientView.as_view(),name='create_client'),
    path('dashbaord/client_page/<slug:slug>',views.client_page,name="client_page"),
    path('dashboard/client_page/<slug:slug>/new_engagement', views.CreateEngagement.as_view(),name="create_engagement"),

]