from rest_framework.routers import DefaultRouter

from example_app.views import (
    SimpleModelViewSet,
    SimpleModelUuidPkViewSet,
    ModelWithForeignKeyFieldViewSet,
    ModelWithManyToManyFieldViewSet,
)

router = DefaultRouter()
router.register("simple-model", SimpleModelViewSet)
router.register("simple-model-uuid-pk", SimpleModelUuidPkViewSet)
router.register("foreign-key-model", ModelWithForeignKeyFieldViewSet)
router.register("many-to-many-model", ModelWithManyToManyFieldViewSet)
urlpatterns = router.urls
