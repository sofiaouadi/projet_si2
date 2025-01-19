from django.shortcuts import render, redirect
from django.db.models import Q
from datetime import date , timedelta
from .models import personnel, service, Contrat


def home(request):
    today = date.today()
    # Récupérer les contrats dont la période d'essai est finie ou proche de la fin
    alertes = Contrat.objects.filter(
        dateD__lte=today,  # Le contrat a déjà commencé
        dateF__gte=today - timedelta(days=30)  # Période d'essai finissant dans les 30 prochains jours
    )

    contrats_a_alertes = []
    for contrat in alertes:
        # Calcul de la fin de la période d'essai
        if contrat.periode_essai:
            periode_essai_fin = contrat.dateD + timedelta(days=contrat.periode_essai)
            # Si la période d'essai est terminée ou proche de se terminer
            if periode_essai_fin <= today:
                contrats_a_alertes.append(contrat)

    return render(request, 'home.html', {'contrats_a_alertes': contrats_a_alertes})

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

#rechercher un contrat
def rechercher_contrats(request):
    query = request.GET.get('q', '')
    contrats = Contrat.objects.filter(
        Q(type__icontains=query) |
        Q(contratEmp__nom__icontains=query) |
        Q(dateD__icontains=query)
    )
    return render(request, 'contrats/recherchercontrats.html', {'contrats': contrats, 'query': query})


# Alerte de fin de contrat
def alertes_contrats(request):
    today = date.today()

    # On suppose que la période d'essai est de 3 mois (par exemple), ajuster selon les règles réelles.
    # Si la période d'essai est à partir du début du contrat
    alertes = Contrat.objects.filter(
        dateD__lte=today,  # Le contrat a déjà commencé
        dateF__gte=today - timedelta(days=30),  # Et la fin de contrat n'est pas dépassée
    )

    contrats_a_alertes = []
    for contrat in alertes:
        # Calcul de la fin de la période d'essai (par exemple, 3 mois après le début du contrat)
        if contrat.periode_essai:
            periode_essai_fin = contrat.dateD + timedelta(days=contrat.periode_essai)
            if periode_essai_fin <= today:
                contrats_a_alertes.append(contrat)
    
    # Vérification des contrats à alerter
    if contrats_a_alertes:
        print(f"Contrats à alerter : {contrats_a_alertes}")
    else:
        print("Aucun contrat à alerter.")

    return render(request, 'contrats/alertes.html', {'contrats_a_alertes': contrats_a_alertes})
