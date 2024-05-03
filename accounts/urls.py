from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path
from .views import *


urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
