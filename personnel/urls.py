from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),  
    path('personnel/', views.liste_personnel, name='personnel'),  
    path('employe/', views.employe, name='employe'),
    path('ajouteremploye/', views.ajouter_employe, name='ajouter_employe'),
    path('contrats/', views.liste_contrats, name='liste_contrats'),
    path('contrats/ajoutercontrat/', views.ajouter_contrat, name='ajouter_contrat'),
    path('contrats/modifiercontrat/<int:contrat_id>/', views.modifier_contrat, name='modifier_contrat'),
    path('contrats/supprimercontrat/<int:contrat_id>/', views.supprimer_contrat, name='supprimer_contrat'),
    path('', views.home, name='home'),
]
