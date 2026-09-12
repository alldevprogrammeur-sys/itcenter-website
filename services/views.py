from django.shortcuts import render , get_object_or_404

# Create your views here.
from .models import Service


def detail(request, slug):
    """
    Vue détail d'un service.

    Récupère le Service à partir de slug_fr, conformément à
    Service.get_absolute_url() qui utilise reverse('services:detail',
    kwargs={'slug': self.slug_fr}).
    """
    service = get_object_or_404(Service, slug_fr=slug)

    context = {
        'service': service,
    }

    return render(request, 'services/detail.html', context)