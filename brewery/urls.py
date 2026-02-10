from django.urls import path
from . import views

app_name = 'brewery'

urlpatterns = [
    path('', views.brewery_list, name='list'),
    path('criar/', views.brewery_create, name='create'),
    path('<int:brewery_id>/', views.brewery_detail, name='detail'),
    path('<int:brewery_id>/editar/', views.brewery_edit, name='edit'),
    path('<int:brewery_id>/deletar/', views.brewery_delete, name='delete'),
]
