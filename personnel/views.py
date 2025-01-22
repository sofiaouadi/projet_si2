from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from datetime import date , timedelta
from .models import personnel, service, Contrat, Favoris, salaire, EvaluationCriteria, PerformanceEvaluation , User , Conges ,personnel, service , SoldeConge , TypeConge ,OffreEmploi, Candidature, Entretien, Absence, Recrutement
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from reportlab.pdfgen import canvas
from .forms import CongeForm , DemandeCongeForm ,OffreEmploiForm, CandidatureForm, EntretienForm
from django.db.models import Q ,Count, Avg
from django.http import HttpResponse
from django.core.exceptions import ValidationError


def home(request):
    return render(request, 'home.html')

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
    query = request.GET.get('q')  # Récupère la valeur du champ de recherche
    contrats = Contrat.objects.all()

    if query:
        # Recherche par nom de l'employé, date de début ou de fin
        contrats = contrats.filter(
            Q(employe__nom__icontains=query) |
            Q(date_debut__icontains=query) |
            Q(date_fin__icontains=query)
        )

    return render(request, 'contrats/recherche.html', {'contrats': contrats, 'query': query})

def detail_contrat(request, contrat_id):
    contrat = get_object_or_404(Contrat, id=contrat_id)
    return render(request, 'contrats/detail.html', {'contrat': contrat})

def imprimer_contrat(request, contrat_id):
    contrat = get_object_or_404(Contrat, id=contrat_id)

    # Créer la réponse HTTP pour un fichier PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Contrat_{contrat.id}.pdf"'

    # Générer le PDF
    p = canvas.Canvas(response)
    p.drawString(100, 800, f"Contrat ID: {contrat.id}")
    p.drawString(100, 780, f"Employé: {contrat.contratEmp}")
    p.drawString(100, 760, f"Date de début: {contrat.dateD}")
    p.drawString(100, 740, f"Date de fin: {contrat.dateF}")
    p.drawString(100, 720, f"Période d'essai: {contrat.periode_essai_fin}")
    p.save()

    return response


def gestion_salaire(request):
    return render(request, 'salaire/salaire.html')

def afficher_salaire(request):
    salaires = salaire.objects.all()
    return render(request, 'salaire/affichersalaire.html', {'salaires': salaires})


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

def contrats_alertes(request):
    contrats = Contrat.objects.filter(periode_essai_fin__gte=date.today()).order_by('periode_essai_fin')
    contrats_avec_alertes = [contrat for contrat in contrats if contrat.alerte_periode_essai()]
    return render(request, 'contrats/alertes.html', {'contrats': contrats_avec_alertes})

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

@login_required
def ajouter_evaluation(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        date_ev = request.POST.get('dateEv')
        commentaire = request.POST.get('comment', '')

        if not employee_id or not date_ev:
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            return redirect('ajouter_evaluation')

        employee = get_object_or_404(personnel, id=employee_id)
        evaluation = PerformanceEvaluation.objects.create(
            employee=employee,
            date=date_ev,
            comments=commentaire
        )

        criteria = EvaluationCriteria.objects.all()
        for criterion in criteria:
            score_value = request.POST.get(f'criteria_{criterion.id}', None)
            if score_value:
                evaluation.scores.create(criterion=criterion, score=score_value)
            else:
                messages.error(request, f"Le score pour le critère '{criterion.name}' ne peut pas être vide.")
                return redirect('ajouter_evaluation')

        messages.success(request, "Évaluation ajoutée avec succès.")
        return redirect('liste_evaluations')

    employees = personnel.objects.all()
    criteria = EvaluationCriteria.objects.all()
    return render(request, 'evaluations/ajouter_evaluation.html', {
        'employees': employees,
        'criteria': criteria
    })

@login_required
def liste_evaluations(request):
    evaluations = PerformanceEvaluation.objects.select_related('employee').prefetch_related('scores__criterion')
    return render(request, 'evaluations/liste_evaluations.html', {'evaluations': evaluations})

@login_required
def rapport_evaluation(request, evaluation_id):
    evaluation = get_object_or_404(PerformanceEvaluation, id=evaluation_id)
    return render(request, 'evaluations/rapport_evaluation.html', {'evaluation': evaluation})

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
        return redirect('ajout')
    return render(request, 'salaire/ajoutersalaire.html', {'employes': employes})

def afficher_salaire(request):
    salaires = salaire.objects.all()
    return render(request, 'salaire/affichersalaire.html', {'salaires': salaires})


def modifier_salaire(request, salaire_id):
    salaire_instance = get_object_or_404(salaire, id=salaire_id)

    if request.method == 'POST':
        salaire_instance.salaireBase = request.POST.get('salaireBase')
        salaire_instance.Prime = request.POST.get('Prime')
        salaire_instance.heure_Sup = request.POST.get('heure_Sup')
        salaire_instance.jourAbsence = request.POST.get('jourAbsence')
        salaire_instance.avance = request.POST.get('avance')
        salaire_instance.salaireF = request.POST.get('salaireF')
        salaire_instance.save()
        return redirect('afficher_salaire')

    return render(request, 'salaire/modifier_salaire.html', {'salaire': salaire_instance})

def supprimer_salaire(request, salaire_id):
    salaire_instance = get_object_or_404(salaire, id=salaire_id)

    if request.method == 'POST':
        salaire_instance.delete()
        return redirect('afficher_salaire')

    return HttpResponse("Méthode non autorisée", status=405)

def liste_conges(request):
    conges = Conges.objects.all()
    types_conge = TypeConge.objects.all()

    type_conge_id = request.GET.get('type_conge')
    if type_conge_id:
        conges = conges.filter(type_conge_id=type_conge_id)

    context = {
        'conges': conges,
        'types_conge': types_conge,
    }
    return render(request, 'conges/liste_conges.html', context)

def ajouter_conge(request):
    if request.method == "POST":
        form = CongeForm(request.POST)
        if form.is_valid():
            conge = form.save(commit=False)

            # Vérifier si un solde de congé existe
            try:
                solde = SoldeConge.objects.get(employe=conge.employe, type_conge=conge.type_conge)
            except SoldeConge.DoesNotExist:
                messages.error(request, "Aucun solde de congé trouvé pour cet employé et ce type de congé.")
                return render(request, "conges/ajouter_conge.html", {"form": form})

            # Calculer les jours pris et valider
            jours_pris = (conge.date_fin - conge.date_debut).days + 1
            if solde.jours_disponibles < jours_pris:
                messages.error(request, "Le solde de congé est insuffisant.")
                return render(request, "conges/ajouter_conge.html", {"form": form})

            solde.jours_disponibles -= jours_pris
            solde.save()
            conge.jours_utilises = jours_pris
            conge.save()

            messages.success(request, "Le congé a été ajouté avec succès.")
            return redirect("liste_conges")
    else:
        form = CongeForm()

    return render(request, "conges/ajouter_conge.html", {"form": form})

def modifier_conge(request, conge_id):
    conge = get_object_or_404(Conges, id=conge_id)

    if request.method == 'POST':
        form = CongeForm(request.POST, instance=conge)
        if form.is_valid():
            form.save()
            messages.success(request, "Le congé a été modifié avec succès.")
            return redirect('liste_conges')
    else:
        form = CongeForm(instance=conge)

    return render(request, 'conges/modifier_conge.html', {'form': form, 'conge': conge})

def demander_conge(request):
    if request.method == "POST":
        form = DemandeCongeForm(request.POST)
        if form.is_valid():
            try:
                conge = form.save(commit=False)
                conge.employe = request.user.personnel  # Associe l'utilisateur connecté
                conge.save()
                messages.success(request, "Votre demande de congé a été soumise avec succès.")
                return redirect("liste_conges")
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = DemandeCongeForm()

    return render(request, "conges/demander_conge.html", {"form": form})

def liste_offres(request):
    offres = OffreEmploi.objects.all()
    return render(request, 'offre/liste_offres.html', {'offres': offres})

def ajouter_offre(request):
    if request.method == 'POST':
        form = OffreEmploiForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_offres')
    else:
        form = OffreEmploiForm()
    return render(request, 'offre/ajouter_offre.html', {'form': form})

def modifier_offre(request, offre_id):
    offre = get_object_or_404(OffreEmploi, id=offre_id)
    if request.method == 'POST':
        form = OffreEmploiForm(request.POST, instance=offre)
        if form.is_valid():
            form.save()
            return redirect('liste_offres')
    else:
        form = OffreEmploiForm(instance=offre)
    return render(request, 'offre/modifier_offre.html', {'form': form})

def supprimer_offre(request, offre_id):
    offre = get_object_or_404(OffreEmploi, id=offre_id)
    if request.method == 'POST':
        offre.delete()
        return redirect('liste_offres')
    return render(request, 'offre/supprimer_offre.html', {'offre': offre})

# Suivi des candidatures
def liste_candidatures(request):
    candidatures = Candidature.objects.all()
    return render(request, 'candidatures/liste_candidatures.html', {'candidatures': candidatures})

def ajouter_candidature(request):
    if request.method == 'POST':
        form = CandidatureForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('liste_candidatures')
    else:
        form = CandidatureForm()
    return render(request, 'candidatures/ajouter_candidatures.html', {'form': form})

# Gestion des entretiens
def planifier_entretien(request, candidature_id):
    candidature = get_object_or_404(Candidature, id=candidature_id)
    if request.method == 'POST':
        form = EntretienForm(request.POST)
        if form.is_valid():
            entretien = form.save(commit=False)
            entretien.candidature = candidature
            entretien.save()
            return redirect('liste_candidatures')
    else:
        form = EntretienForm()
    return render(request, 'entretien/planifier_entretien.html', {'form': form, 'candidature': candidature})

def gestion_rec(request):
    return render(request, 'gestion_rec.html')

def dashboard(request):
    # Analyse des employés
    total_employes = personnel.objects.count()
    employes_par_type_contrat = personnel.objects.values('type_contrat').annotate(count=Count('id'))
    repartition_sexe = personnel.objects.values('sexe').annotate(count=Count('id'))

    # Top performeurs
    top_performeurs = personnel.objects.order_by('-score_evaluation')[:5]

    # Analyse des absences
    absences = Absence.objects.values('date_absence').annotate(count=Count('id')).order_by('-count')[:12]


    context = {
        'total_employes': total_employes,
        'employes_par_type_contrat': employes_par_type_contrat,
        'repartition_sexe': repartition_sexe,
        'top_performeurs': top_performeurs,
        'absences': absences,
    }

    return render(request, 'dashboard.html', context)