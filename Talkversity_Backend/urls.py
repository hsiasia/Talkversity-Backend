"""Talkversity_Backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Talkversity API",
        default_version='v1',
        description="API for Talkversity",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@contact.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', TemplateView.as_view(template_name='500.html')),
    path('admin/', admin.site.urls),
    path('api/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # doc
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', include('target.urls')),  # target related url
    path('', include('login.urls')),  # login related url
    path('', include('scenario.urls')),  # scenario related url
    path('', include('article.urls')),  # article related url
    path('', include('sound.urls')),  # sound related url
    path('', include('achievements.urls')),  # achievements related url
    path('', include('records.urls')),  # record related url
    path('', include('pretest.urls')),  # pretest related url
    path('', include('face.urls')),  # face related url
]

handler404 = 'login.views.handler404'
handler500 = 'login.views.handler500'
