from django.shortcuts import render , get_object_or_404

# Create your views here.
from .models import Formation


def detail(request, slug):
    """
    Vue détail d'une formation.

    Récupère la Formation à partir de slug_fr, conformément à
    Formation.get_absolute_url() qui utilise reverse('formations:detail',
    kwargs={'slug': self.slug_fr}).
    """
    formation = get_object_or_404(Formation, slug_fr=slug)

    context = {
        'formation': formation,
    }

    return render(request, 'formations/detail.html', context)
