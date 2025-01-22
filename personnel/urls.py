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
    path('ajouter/', views.ajouter_salaire, name='ajout'),
    path('contrats/', views.liste_contrats, name='liste_contrats'),
    path('contrats/ajoutercontrat/', views.ajouter_contrat, name='ajouter_contrat'),
    path('contrats/modifiercontrat/<int:contrat_id>/', views.modifier_contrat, name='modifier_contrat'),
    path('contrats/supprimercontrat/<int:contrat_id>/', views.supprimer_contrat, name='supprimer_contrat'),
    path('favoris/', views.favoris_view, name='favoris'),  # Page pour afficher les favoris
    path('add_favoris/', views.add_favoris, name='add_favoris'),  # Ajouter aux favoris
    path('remove_favoris/', views.remove_favoris, name='remove_favoris'),  # Supprimer des favoris
    path('contrats/alertes/', views.contrats_alertes, name='contrats_alertes'),
    path('evaluations/liste', views.liste_evaluations, name='liste_evaluations'),
    path('evaluations/ajouter/', views.ajouter_evaluation, name='ajouter_evaluation'),
    path('evaluations/rapport/<int:evaluation_id>/', views.rapport_evaluation, name='rapport_evaluation'),
    path('contrats/recherchercontrat/', views.rechercher_contrats, name='rechercher_contrats'),
    path('contrats/detail/<int:contrat_id>/', views.detail_contrat, name='detail_contrat'),
    path('contrats/imprimer/<int:contrat_id>/imprimer/', views.imprimer_contrat, name='imprimer_contrat'),
    path('modifier_salaire/<int:salaire_id>/', views.modifier_salaire, name='modifier_salaire'),
    path('supprimer_salaire/<int:salaire_id>/', views.supprimer_salaire, name='supprimer_salaire'),
    path('conges/liste/', views.liste_conges, name='liste_conges'),
    path('conges/ajouter/', views.ajouter_conge, name='ajouter_conge'),
    path('conges/modifier/', views.modifier_conge, name='modifier_conge'),
    path('conges/demander/', views.demander_conge, name='demander_conge'),
    path('offres/', views.liste_offres, name='liste_offres'),
    path('gestion_rec/', views.gestion_rec, name='gestion_rec'),
    path('offres/ajouter/', views.ajouter_offre, name='ajouter_offre'),
    path('offres/modifier/<int:offre_id>/', views.modifier_offre, name='modifier_offre'),
    path('offres/supprimer/<int:offre_id>/', views.supprimer_offre, name='supprimer_offre'),
    path('candidatures/', views.liste_candidatures, name='liste_candidatures'),
    path('candidatures/ajouter/', views.ajouter_candidature, name='ajouter_candidature'),
    path('entretiens/planifier/<int:candidature_id>/', views.planifier_entretien, name='planifier_entretien'),
    path('dashboard/', views.dashboard, name='dashboard')
]
