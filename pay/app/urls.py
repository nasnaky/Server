from django.urls import path, include
from .views import *

from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)

urlpatterns = [
    path('user/login/', TokenObtainPairView.as_view()),
    path('user/register/', UserRegistrationView.as_view()),
    path('user/', include('dj_rest_auth.urls')),
    path('Product/', ProductView.as_view()),
    path('Product/list/', ProductListView.as_view()),
    path('Product/search', ProductSearchView.as_view(), name='product-search'),
    path('Product/<int:pk>/', ProductDetailView.as_view()),
]

urlpatterns += static('/media/', document_root=settings.MEDIA_ROOT)
