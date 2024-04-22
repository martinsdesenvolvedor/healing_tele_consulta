from django.urls import path
from . import views 

urlpatterns = [
   path('cadastro/', views.cadastro, name='cadastro'),
   path('login/', views.logar, name='logar'),
   path('logout/', views.deslogar, name='deslogar'),
  
]