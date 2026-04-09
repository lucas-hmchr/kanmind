from django.urls import path
from rest_framework.routers import DefaultRouter

from boards_app.api.views import BoardViewSet, EmailCheckView

router = DefaultRouter(trailing_slash=True)
router.register("boards", BoardViewSet, basename="boards")

urlpatterns = [
    path("email-check/", EmailCheckView.as_view(), name="email-check"),
]

urlpatterns += router.urls