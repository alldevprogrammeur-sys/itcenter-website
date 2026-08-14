# Create your views here.
from django.shortcuts import render
from django.utils.translation import get_language

# Import models from the apps mentioned in the project.
# We only use fields that actually exist on the models provided.
from formations.models import Formation
from realisations.models import Realisation
from contact.models import Temoignage


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

    # Témoignages validés — utiliser uniquement le champ réel 'est_valide'
    # On met en avant les témoignages marqués mise_en_avant, puis les plus récents.
    temoignages = Temoignage.objects.filter(est_valide=True).order_by('-mise_en_avant', '-created_at')

    # Récupérer quelques formations et réalisations mises en avant si les champs existent.
    featured_formations = Formation.objects.filter(est_active=True, mise_en_avant=True).order_by('-ordre_affichage')[:3]
    featured_realisations = Realisation.objects.filter(est_active=True, mise_en_avant=True).order_by('-ordre_affichage')[:3]

    context = {
        "formations_active_count": formations_active_count,
        "formations_certifiantes_count": formations_certifiantes_count,
        "realisations_active_count": realisations_active_count,
        "temoignages": temoignages,
        "featured_formations": featured_formations,
        "featured_realisations": featured_realisations,
        # Pass current language to template to choose francophone/english fields
        "current_language": get_language(),
    }

    return render(request, "core/welcome.html", context)
