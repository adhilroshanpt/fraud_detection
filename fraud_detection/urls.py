"""
URL configuration for fraud_detection project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from fraud_detection_app import views
from django.conf import settings
from django.conf.urls.static import static
from fraud_detection_app.views import get_third_party_apps

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user_login',views.UserLoginView.as_view(),name='userlogin_view'),
    path('user/logout',views.UserLogoutView.as_view(),name='userlogout_view'),
    path('user_register',views.UserRegisterView.as_view(),name='user_register'),
    path('admin_dashboard',views.AdminDashboardView.as_view(),name='dashboard'),
    path('admin_login',views.AdminLoginView.as_view(),name='adminlogin_view'),
    path('user_managment',views.UserManagmentView.as_view(),name='usermanagment_view'),
    path('application',views.ApplicationView.as_view(),name='application_view'),
    path('activities',views.ActivitiesView.as_view(),name='activities_view'),
    path('user_dashboard',views.UserDashboardView.as_view(),name='userdashboard_view'),
    path('scan_app',views.ScanAppView.as_view(),name='scanapp_view'),
    path('scanning',views.ScanningView.as_view(),name='scanning_view'),
    path('result',views.ResultView.as_view(),name='result_view'),
    path('test',views.TesView.as_view(),name='test_view'),
    path('test2',views.Test2View.as_view(),name='test2_view'),
    path('api/external-apps/', get_third_party_apps, name='third_party_apps'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
