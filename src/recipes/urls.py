from rest_framework.routers import DefaultRouter

from recipes.views import RecipeViewSet

router = DefaultRouter()
router.register("recipes", RecipeViewSet)

urlpatterns = router.urls
