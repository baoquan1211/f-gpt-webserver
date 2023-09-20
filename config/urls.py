"""
URL configuration for webserver project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from conversations.urls import urlpattern as conversation_urls
from users.urls import urlpatterns as user_urls
from policies.urls import urlpatterns as policy_urls
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView
from users.views import TokenObtainPairView

urlpatterns = [
    path("admin", admin.site.urls),
    path("api/v1/conversations", include(conversation_urls)),
    path("api/v1/policies", include(policy_urls)),
    path("api/v1/", include(user_urls)),
    path("api/login", TokenObtainPairView.as_view(), name="login"),
    path("api/refresh", TokenRefreshView.as_view(), name="refresh"),
    path("api/logout", TokenBlacklistView.as_view(), name="logout"),
]
