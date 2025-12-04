from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, ConsultationViewSet

# Создаем роутер
router = DefaultRouter()

# --- ВОТ ЭТИХ СТРОК СКОРЕЕ ВСЕГО НЕ ХВАТАЕТ ---
router.register(r'patients', PatientViewSet)
router.register(r'consultations', ConsultationViewSet)
# ---------------------------------------------

urlpatterns = [
    path('', include(router.urls)),
]