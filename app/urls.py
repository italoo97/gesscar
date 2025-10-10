"""
URL configuration for Gesscar project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf.urls.static import static
from django.conf import settings
from accounts.views import auth_page_view, ProcessarFormularioView
from cars import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ProcessarFormularioView.as_view(), name='index'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('login', auth_page_view, name='login'),
    path('register', auth_page_view, name='register'),
    path('processar-formulario', ProcessarFormularioView.as_view(), name='processar-formulario'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
