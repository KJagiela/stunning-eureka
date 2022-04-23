from django.conf import settings

from rest_framework.routers import (
    DefaultRouter,
    SimpleRouter,
)

router: SimpleRouter
if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()


app_name = 'api'
urlpatterns = router.urls
