from django.shortcuts import render, get_object_or_404

# Create your views here.
from .models import Realisation


def detail(request, slug):
    """
    Vue détail d'une réalisation.

    Récupère la Realisation à partir de slug_fr, conformément à
    Realisation.get_absolute_url() qui utilise reverse('realisations:detail',
    kwargs={'slug': self.slug_fr}).
    """
    realisation = get_object_or_404(Realisation, slug_fr=slug)

    context = {
        'realisation': realisation,
    }

    return render(request, 'realisations/detail.html', context)
