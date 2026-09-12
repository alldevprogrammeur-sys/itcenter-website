# core/views.py
from django.shortcuts import render
from django.utils.translation import get_language
from django.db.models import Sum

# Import models from the apps mentioned in the project.
from core.models import ParametreSite, APropos, Valeur, DomaineExpertise
from formations.models import Formation, Inscription
from services.models import Service
from realisations.models import Realisation
from contact.models import Temoignage, Partenaire


def welcome(request):
    """
    Welcome page view — wiring between DB and template.

    Context provided:
      - formations_active_count: number of Formation with est_active=True
      - formations_certifiantes_count: number of Formation with certificat=True
      - realisations_active_count: number of Realisation with est_active=True
      - temoignages: QuerySet of Temoignage objects that are validated (est_valide=True),
                    ordered with mise_en_avant first then newest.
      - featured_formations: up to 3 formations where mise_en_avant=True and est_active=True
      - featured_realisations: up to 3 realisations where mise_en_avant=True and est_active=True
    """
    formations_active_count = Formation.objects.filter(est_active=True).count()
    formations_certifiantes_count = Formation.objects.filter(certificat=True).count()
    realisations_active_count = Realisation.objects.filter(est_active=True).count()

    temoignages = Temoignage.objects.filter(est_valide=True).order_by('-mise_en_avant', '-created_at')

    featured_formations = Formation.objects.filter(est_active=True, mise_en_avant=True).order_by('-ordre_affichage')[:3]
    featured_realisations = Realisation.objects.filter(est_active=True, mise_en_avant=True).order_by('-ordre_affichage')[:3]

    context = {
        "formations_active_count": formations_active_count,
        "formations_certifiantes_count": formations_certifiantes_count,
        "realisations_active_count": realisations_active_count,
        "temoignages": temoignages,
        "featured_formations": featured_formations,
        "featured_realisations": featured_realisations,
        "current_language": get_language(),
    }

    return render(request, "core/welcome.html", context)


def accueil(request):
    """
    Vue de la page Accueil.

    Le Hero est volontairement statique dans le template accueil.html
    (pas de modèle HeroAccueil, rien à récupérer ici pour cette section).
    """

    # --- Paramètres du site (singleton) ---
    parametres_site = ParametreSite.get_solo()

    # --- À propos (singleton) + valeurs liées ---
    apropos = APropos.get_solo()
    if apropos is not None:
        valeurs = apropos.valeurs.filter(actif=True)
    else:
        valeurs = Valeur.objects.none()

    # --- Domaines d'expertise ---
    domaines_expertise = DomaineExpertise.objects.filter(actif=True)

    # --- Formations mises en avant ---
    formations_accueil = (
        Formation.objects
        .filter(est_active=True, mise_en_avant=True)
        .select_related('categorie', 'formateur')
    )

    # --- Services mis en avant ---
    services_accueil = (
        Service.objects
        .filter(est_active=True, mise_en_avant=True)
        .select_related('categorie')
    )

    # --- Réalisations mises en avant ---
    # est_confidentiel est conservé tel quel : la logique d'affichage
    # du nom du client masqué reste gérée par le template.
    realisations_accueil = (
        Realisation.objects
        .filter(est_active=True, mise_en_avant=True)
        .select_related('categorie')
    )

    # --- Statistiques ---
    formations_total = Formation.objects.filter(est_active=True).count()
    formations_certifiantes = Formation.objects.filter(est_active=True, certificat=True).count()
    realisations_total = Realisation.objects.filter(est_active=True).count()

    # Participants = SOMME de nombre_participants, pas un COUNT d'inscriptions.
    # Coalesce via 'or 0' pour ne jamais transmettre None au template.
    participants_total = Inscription.objects.aggregate(
        total=Sum('nombre_participants')
    )['total'] or 0

    # --- Témoignages mis en avant et validés ---
    temoignages_accueil = Temoignage.objects.filter(est_valide=True, mise_en_avant=True)

    # --- Partenaires actifs ---
    partenaires_accueil = Partenaire.objects.filter(est_actif=True)

    context = {
        'parametres_site': parametres_site,
        'apropos': apropos,
        'valeurs': valeurs,
        'domaines_expertise': domaines_expertise,
        'formations_accueil': formations_accueil,
        'services_accueil': services_accueil,
        'realisations_accueil': realisations_accueil,

        'formations_total': formations_total,
        'participants_total': participants_total,
        'formations_certifiantes': formations_certifiantes,
        'realisations_total': realisations_total,

        'temoignages_accueil': temoignages_accueil,
        'partenaires_accueil': partenaires_accueil,

        'current_language': get_language(),
    }

    return render(request, "core/accueil.html", context)