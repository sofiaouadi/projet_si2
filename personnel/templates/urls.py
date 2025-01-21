from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),  # Page de connexion
    path('logout/', views.logout_view, name='logout'),  # Déconnexion
    path('home/', views.home, name='home'),   
    path('personnel/', views.liste_personnel, name='personnel'),
    path('modifier-employe/<int:emp_id>/', views.modifier_employe, name='modifier_employe'),
    path('supprimer-employe/<int:emp_id>/', views.supprimer_employe, name='supprimer_employe'),
    path('employe/', views.employe, name='employe'),
    path('ajouteremploye/', views.ajouter_employe, name='ajouter_employe'),
    path('gestion/', views.gestion_salaire, name='gestion_salaire'),
    path('afficher/', views.afficher_salaire, name='afficher_salaire'),
    path('ajouter/', views.ajouter_salaire, name='ajouter_salaire'),
    path('contrats/', views.liste_contrats, name='liste_contrats'),
    path('contrats/ajoutercontrat/', views.ajouter_contrat, name='ajouter_contrat'),
    path('contrats/modifiercontrat/<int:contrat_id>/', views.modifier_contrat, name='modifier_contrat'),
    path('contrats/supprimercontrat/<int:contrat_id>/', views.supprimer_contrat, name='supprimer_contrat'),
    path('favoris/', views.favoris_view, name='favoris'),  # Page pour afficher les favoris
    path('add_favoris/', views.add_favoris, name='add_favoris'),  # Ajouter aux favoris
    path('remove_favoris/', views.remove_favoris, name='remove_favoris'),  # Supprimer des favoris
    path('contrats/alertes/', views.alertes_contrats, name='alertes_contrats'),
]