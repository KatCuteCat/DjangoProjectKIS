from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    StudentViewSet,
    StipendTypeViewSet,
    StipendApplicationViewSet,
    ApplicationHistoryViewSet
)

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'stipend-types', StipendTypeViewSet, basename='stipendtype')
router.register(r'applications', StipendApplicationViewSet, basename='stipendapplication')
router.register(r'history', ApplicationHistoryViewSet, basename='applicationhistory')


urlpatterns = [
    path('', include(router.urls)),
    path('export-applications/', StipendApplicationViewSet.as_view({'get': 'export_to_excel'}), name='export-applications'),
]