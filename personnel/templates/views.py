from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from datetime import date , timedelta
from .models import personnel, service, Contrat, Favoris, salaire
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


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

def supprimer_employe(request, emp_id):
    emp = get_object_or_404(personnel, id=emp_id)

    if request.method == 'POST':
        emp.delete()
        return redirect('personnel')

    return render(request, 'confirmer_suppression.html', {'employe': emp})


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

def modifier_employe(request, emp_id):
    emp = get_object_or_404(personnel, id=emp_id)

    if request.method == 'POST':
        emp.nom = request.POST.get('nom')
        emp.prenom = request.POST.get('prenom')
        emp.dateN = request.POST.get('dateN')  # Assurez-vous que le champ "date de naissance" est bien présent
        emp.numT = request.POST.get('numT')  # Numéro de téléphone
        emp.email = request.POST.get('email')
        emp.posteOccupe = request.POST.get('posteOccupe')
        emp.dateEmbauche = request.POST.get('dateEmbauche')
        emp.adresse = request.POST.get('adresse')

        # Mise à jour du service lié
        service_nom = request.POST.get('serviceEmp')
        service_obj, created = service.objects.get_or_create(nom=service_nom)
        emp.serviceEmp = service_obj

        emp.save()
        return redirect('personnel')

    return render(request, 'modifier_employe.html', {'employe': emp})

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


def rechercher_contrats(request):
    query = request.GET.get('q', '')
    contrats = Contrat.objects.filter(
        Q(type__icontains=query) |
        Q(contratEmp__nom__icontains=query) |
        Q(dateD__icontains=query)
    )
    return render(request, 'contrats/recherchercontrats.html', {'contrats': contrats, 'query': query})

def gestion_salaire(request):
    return render(request, 'salaire/salaire.html')

def afficher_salaire(request):
    salaires = salaire.objects.all()
    return render(request, 'salaire/affichersalaire.html', {'salaires': salaires})

def ajouter_salaire(request):
    employes = personnel.objects.all()
    if request.method == 'POST':
        employe_id = request.POST['employe']
        employe = personnel.objects.get(id=employe_id)
        salaire_base = float(request.POST['salaireBase'])
        prime = float(request.POST.get('prime', 0))
        heure_sup = float(request.POST.get('heureSup', 0))
        avance = float(request.POST.get('avance', 0))
        jour_absence = float(request.POST.get('jourAbsence', 0))
        salaire_final = salaire_base + prime + heure_sup - (avance + jour_absence * 100)

        salaire.objects.create(
            SalaireEmp=employe,
            salaireBase=salaire_base,
            Prime=prime,
            heure_Sup=heure_sup,
            avance=avance,
            jourAbsence=jour_absence,
            salaireF=salaire_final
        )
        return redirect('afficher_salaire')
    return render(request, 'salaire/ajoutersalaire.html', {'employes': employes})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Rediriger vers la page d'accueil
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")  # Message d'erreur
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def home_view(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Rediriger vers la page de connexion si non authentifié
    return render(request, 'home.html')


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

@login_required
def favoris_view(request):
    favoris = Favoris.objects.filter(user=request.user)
    return render(request, 'favoris.html', {'favoris': favoris})

@login_required
def add_favoris(request):
    if request.method == 'POST':
        name = request.POST['name']
        link = request.POST['link']
        Favoris.objects.create(user=request.user, name=name, link=link)
    return redirect('favoris')

@login_required
def remove_favoris(request):
    if request.method == 'POST':
        link = request.POST['link']
        Favoris.objects.filter(user=request.user, link=link).delete()
    return redirect('favoris')