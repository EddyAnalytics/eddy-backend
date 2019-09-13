from django.urls import path

from . import views

app_name = 'debezium_connectors'
urlpatterns = [
    path('', views.DebeziumConnectorListView.as_view(), name='list'),
    path('<pk>/', views.DebeziumConnectorDetailView.as_view(), name='detail'),
]
