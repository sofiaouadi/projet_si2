from django.shortcuts import render, redirect
from django.db.models import Q
from datetime import date , timedelta
from .models import personnel, service, Contrat


def home(request):
    # Récupérer les contrats proches de la fin de période d'essai (30 jours avant)
    today = date.today()
    alertes_contrats = Contrat.objects.filter(fin_periode_essai__lte=today + timedelta(days=30))

    return render(request, 'home.html', {'alertes_contrats': alertes_contrats})

def liste_personnel(request):  # Changer le nom pour éviter le conflit
    # ✅ Récupérer tous les employés avec leur service
    personnel_list = personnel.objects.select_related('serviceEmp').all()

    return render(request, 'personnel.html', {'personnel': personnel_list})

def employe(request):
    return render(request, 'employe.html')

def ajouter_employe(request):
    if request.method == 'POST':
        nom = request.POST['nom']
        prenom = request.POST['prenom']
        dateN = request.POST['dateN']
        numT = request.POST['numT']
        email = request.POST['email']
        posteOccupe = request.POST['posteOccupe']
        dateEmbauche = request.POST['dateEmbauche']
        adresse = request.POST['adresse']
        serviceEmp_nom = request.POST['serviceEmp']

        serviceEmp, created = service.objects.get_or_create(nom=serviceEmp_nom)
        personnel.objects.create(
            nom=nom,
            prenom=prenom,
            dateN=dateN,
            numT=numT,
            email=email,
            posteOccupe=posteOccupe,
            dateEmbauche=dateEmbauche,
            adresse=adresse,
            serviceEmp=serviceEmp
        )
        return redirect('personnel')
    return render(request, 'ajouteremploye.html')

#lister les contrats
def liste_contrats(request):
    contrats = Contrat.objects.select_related('contratEmp').all()
    return render(request, 'contrats/listecontrats.html', {'contrats': contrats})

#ajouter un contrat
def ajouter_contrat(request):
    if request.method == 'POST':
        type_contrat = request.POST['type']
        dateD = request.POST['dateD']
        dateF = request.POST['dateF']
        salaire = request.POST['salaire']
        employe_id = request.POST['employe']

        employe = personnel.objects.get(id=employe_id)
        Contrat.objects.create(
            type=type_contrat,
            dateD=dateD,
            dateF=dateF,
            salaire=salaire,
            contratEmp=employe
        )
        return redirect('liste_contrats')

    employes = personnel.objects.all()
    return render(request, 'contrats/ajoutercontrat.html', {'employes': employes})

#modifier un contrat
def modifier_contrat(request, contrat_id):
    contrat = Contrat.objects.get(id=contrat_id)
    if request.method == 'POST':
        contrat.type = request.POST['type']
        contrat.dateD = request.POST['dateD']
        contrat.dateF = request.POST['dateF']
        contrat.salaire = request.POST['salaire']
        employe_id = request.POST['employe']
        contrat.contratEmp = personnel.objects.get(id=employe_id)
        contrat.save()
        return redirect('liste_contrats')

    employes = personnel.objects.all()
    return render(request, 'contrats/modifiercontrat.html', {'contrat': contrat, 'employes': employes})

#supprimer un contrat (archiver)
def supprimer_contrat(request, contrat_id):
    contrat = Contrat.objects.get(id=contrat_id)
    if request.method == 'POST':
        contrat.delete()
        return redirect('liste_contrats')
    return render(request, 'contrats/supprimercontrat.html', {'contrat': contrat})

#alerte de fin de contrat
def alertes_contrats(request):
    # Alertes sur les contrats proches de la fin de période d'essai
    today = date.today()
    alertes = Contrat.objects.filter(
        date_debut__lte=today,  # Le contrat a déjà commencé
        date_debut__gte=today - timedelta(days=30),  # Si la période d'essai va finir dans les 30 prochains jours
    )
 # Récupère les contrats dont la période d'essai va bientôt se terminer
    contrats_a_alertes = []
    for contrat in alertes:
        if contrat.fin_periode_essai <= today:
            contrats_a_alertes.append(contrat)

    return render(request, 'contrats/alertes.html', {'contrats_a_alertes': contrats_a_alertes})