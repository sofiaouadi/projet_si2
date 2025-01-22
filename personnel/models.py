from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from datetime import timedelta, date
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

# Create your models here conges

class service(models.Model):
 nom= models.CharField(max_length=50)
 description= models.CharField(max_length=300)
 def __str__(self):
        return self.nom

class personnel(models.Model):
    nom = models.CharField(max_length=50)  
    prenom = models.CharField(max_length=50 )
    dateN = models.DateField(null=True, blank=True)  
    numT = models.FloatField(null=True, blank=True)  
    email = models.CharField(max_length=100)
    sexe = models.CharField(max_length=10,null=True, blank=True, choices=[('M', 'Homme'), ('F', 'Femme')])
    age = models.IntegerField(null=True, blank=True)
    posteOccupe = models.CharField(max_length=50) 
    date_embauche = models.DateField(null=True, blank=True) 
    type_contrat = models.CharField(max_length=20,null=True, blank=True, choices=[('CDI', 'CDI'), ('CDD', 'CDD'), ('Stagiaire', 'Stagiaire')])
    adresse = models.TextField(null=True, blank=True)
    serviceEmp = models.ForeignKey(service, on_delete=models.CASCADE, null=True, blank=True)
    score_evaluation = models.FloatField(null=True, blank=True)
    def __str__(self):
        return self.nom
    

 
class Contrat(models.Model):
    TYPE_CONTRAT_CHOICES = [
        ('CDI', 'Contrat à Durée Indéterminée'),
        ('CDD', 'Contrat à Durée Déterminée'),
        ('Stage', 'Stage'),
        ('Autre', 'Autre'),  
    ]
    type = models.CharField(max_length=50, choices = TYPE_CONTRAT_CHOICES, default = 'CDI')
    dateD = models.DateField(null=True, blank=True)
    dateF = models.DateField(null=True, blank=True)
    salaire = models.FloatField(null=True, blank=True)  # Supprimez max_length
    contratEmp = models.ForeignKey(personnel, on_delete=models.CASCADE)
    periode_essai_fin = models.DateField(null=True, blank=True)
    est_renouvelle = models.DateField(null=True, blank=True)

class Command(BaseCommand):
    help = 'Envoie des alertes pour les périodes d\'essai proches de leur fin'

    def handle(self, *args, **kwargs):
        alertes = Contrat.objects.filter(
            periode_essai_fin__gte=date.today(),
            periode_essai_fin__lte=date.today() + timedelta(days=7)
        )
        for contrat in alertes:
            print(f"Alerte: La période d'essai du contrat de {contrat.employe.nom} se termine bientôt ({contrat.periode_essai_fin}).")
    
def clean(self):
        """Validation pour vérifier que dateF est après dateD."""
        if self.dateF and self.dateD and self.dateF <= self.dateD:
            raise ValidationError("La date de fin doit être postérieure à la date de début.")

def __str__(self):
        return f"{self.type} - {self.contratEmp.nom} ({self.dateD} à {self.dateF})"

def alerte_periode_essai(self):
        if self.periode_essai_fin:
            aujourd_hui = date.today()
            delta = self.periode_essai_fin - aujourd_hui
            return delta.days <= 7 and delta.days >= 0  # Alerte 7 jours avant la fin
        return False

class evaluation(models.Model):
    dateEv = models.DateField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)  # Supprimez max_length
    commentaire = models.CharField(max_length=300,null=True, blank=True)
    evalueremp = models.ForeignKey(personnel, on_delete=models.CASCADE)


class salaire(models.Model):
    salaireBase = models.FloatField(null=True, blank=True)  # Supprimez max_length
    Prime = models.FloatField(null=True, blank=True)
    heure_Sup = models.FloatField(null=True, blank=True)
    avance = models.FloatField(null=True, blank=True)
    jourAbsence = models.FloatField(null=True, blank=True)
    salaireF = models.FloatField(null=True, blank=True)
    SalaireEmp = models.ForeignKey(personnel, on_delete=models.CASCADE)

class Favoris(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)  # Nom de la section
    link = models.CharField(max_length=255)  # URL de la section

    def str(self):
        return f"{self.user.username} - {self.name}"

class EvaluationCriteria(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    weight = models.FloatField(default=1.0)

    def __str__(self):
        return self.name

class PerformanceEvaluation(models.Model):
    employee = models.ForeignKey(personnel, on_delete=models.CASCADE)
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    period = models.CharField(max_length=50, choices=[('Annual', 'Annual'), ('Semi-annual', 'Semi-annual')])
    criteria_scores = models.JSONField()
    comments = models.TextField(blank=True)

    def calculate_total_score(self):
        total_score = sum(score * criterion['weight'] for criterion, score in self.criteria_scores.items())
        return total_score

    def __str__(self):
        return f"{self.employee.nom} - {self.date}"

class TypeConge(models.Model):
    TYPE_CHOICES = [
        ('annuel', 'Annuel'),
        ('maladie', 'Maladie'),
        ('maternite', 'Maternité'),
        ('paternite', 'Paternité'),
        ('sans_solde', 'Sans Solde'),
    ]

    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    cumulable = models.BooleanField(default=True)
    max_jours_annuels = models.IntegerField()

    def __str__(self):
        return self.type

class SoldeConge(models.Model):
    employe = models.ForeignKey(personnel, on_delete=models.CASCADE,null=True, blank=True, related_name="soldes")
    type_conge = models.ForeignKey(TypeConge, on_delete=models.CASCADE, related_name="soldes")
    jours_disponibles = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    jours_cumules = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.employe.nom} - {self.type_conge.type} : {self.jours_disponibles} jours"

class Conges(models.Model):
    employe = models.ForeignKey(personnel, on_delete=models.CASCADE,null=True, blank=True, related_name="conges")
    type_conge = models.ForeignKey(TypeConge, on_delete=models.CASCADE, null=True)
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    jours_utilises = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def valider(self):
        if self.date_debut > self.date_fin:
            raise ValidationError("La date de début doit être antérieure ou égale à la date de fin.")

        jours_demande = (self.date_fin - self.date_debut).days + 1

        try:
            solde = SoldeConge.objects.get(employe=self.employe, type_conge=self.type_conge)
        except SoldeConge.DoesNotExist:
            raise ValidationError("Aucun solde de congé trouvé pour cet employé et ce type de congé.")

        if solde.jours_disponibles < jours_demande:
            raise ValidationError("Le solde de congé est insuffisant pour ce type de congé.")

    def save(self, *args, **kwargs):
        self.valider()

        jours_demande = (self.date_fin - self.date_debut).days + 1
        solde = SoldeConge.objects.get(employe=self.employe, type_conge=self.type_conge)
        solde.jours_disponibles -= jours_demande
        solde.save()

        self.jours_utilises = jours_demande
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employe.nom} - {self.type_conge.type} : {self.jours_utilises} jours"
        
class Recrutement(models.Model):
    date_recrutement = models.DateField(null=True, blank=True)
    type_contrat = models.CharField(max_length=20,null=True, blank=True, choices=[('CDI', 'CDI'), ('CDD', 'CDD'), ('Stagiaire', 'Stagiaire')])
    posteRecru = models.CharField(max_length=50,null=True, blank=True)
    statutrecrutement = models.CharField(max_length=50,null=True, blank=True)

class OffreEmploi(models.Model):
    titre = models.CharField(max_length=200)
    description = models.TextField()
    date_publication = models.DateField(auto_now_add=True)
    date_expiration = models.DateField()
    statut = models.BooleanField(default=True)  # Indique si l'offre est active ou non

    def __str__(self):
        return self.titre

class Candidature(models.Model):
    STATUT_CHOICES = [
        ('reçue', 'Reçue'),
        ('en_cours', 'En cours de traitement'),
        ('acceptée', 'Acceptée'),
        ('rejetée', 'Rejetée'),
    ]

    offre = models.ForeignKey(OffreEmploi, on_delete=models.CASCADE, related_name="candidatures")
    nom_candidat = models.CharField(max_length=100)
    email_candidat = models.EmailField()
    cv = models.FileField(upload_to='cvs/')  # Stockage des fichiers de CV
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='reçue')
    date_soumission = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Candidature de {self.nom_candidat} pour {self.offre.titre}"

class Entretien(models.Model):
    candidature = models.OneToOneField(Candidature, on_delete=models.CASCADE, related_name="entretien")
    date_entretien = models.DateTimeField()
    commentaires = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Entretien pour {self.candidature.nom_candidat}"

class Absence(models.Model):
    personnel = models.ForeignKey(personnel, on_delete=models.CASCADE)
    date_absence = models.DateField()

