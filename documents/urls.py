from django.urls import path
from .views import generate_document, retrieve_document

urlpatterns = [
    path('generate/', generate_document, name='generate_document'),
    path('retrieve/<uuid:unique_code>/', retrieve_document, name='retrieve_document'),
]
