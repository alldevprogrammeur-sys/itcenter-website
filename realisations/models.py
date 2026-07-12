from django.db import models

# Create your models here.
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class TimestampedModel(models.Model):
    """
    Modèle abstrait fournissant created_at / updated_at.
    """
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Realisation(TimestampedModel):
    TYPE_REALISATION_CHOICES = (
        ('reseau_informatique', _('Réseau informatique')),
        ('developpement_web', _('Développement Web')),
        ('developpement_mobile', _('Développement Mobile')),
        ('developpement_desktop', _('Développement Desktop')),
        ('cybersecurite', _('Cybersécurité')),
        ('camera_surveillance', _('Caméras de surveillance')),
        ('telephonie_ip', _('Téléphonie IP/VoIP')),
        ('administration_systeme', _('Administration Système')),
        ('formation', _('Formation')),
        ('autre', _('Autre')),
    )

    BADGE_CHOICES = (
        ('nouveau', _('Nouveau')),
        ('projet_phare', _('Projet phare')),
        ('populaire', _('Populaire')),
        ('aucun', _('Aucun')),
    )

    reference = models.CharField(_('Référence'), max_length=100, unique=True, db_index=True)
    nom_fr = models.CharField(_('Nom (FR)'), max_length=255, db_index=True)
    nom_en = models.CharField(_('Nom (EN)'), max_length=255, blank=True)
    slug_fr = models.SlugField(_('Slug (FR)'), max_length=255, unique=True, db_index=True)
    slug_en = models.SlugField(_('Slug (EN)'), max_length=255, unique=True, db_index=True)

    categorie = models.ForeignKey(
        'core.Categorie',
        on_delete=models.PROTECT,
        related_name='realisations',
        verbose_name=_('Catégorie')
    )

    # Présentation
    description_fr = models.TextField(_('Description (FR)'), blank=True)
    description_en = models.TextField(_('Description (EN)'), blank=True)

    # Résumé
    resume_fr = models.TextField(_('Résumé (FR)'), blank=True)
    resume_en = models.TextField(_('Résumé (EN)'), blank=True)

    # Illustration
    image_principale = models.ImageField(
        _('Image principale'),
        upload_to='realisations/images/',
        blank=True,
        null=True
    )
    video_presentation = models.URLField(
        _('Vidéo de présentation (YouTube/Vimeo)'),
        blank=True,
        help_text=_('URL de la vidéo de présentation (YouTube ou Vimeo).')
    )

    # Informations du projet
    client = models.CharField(_('Client'), max_length=255, blank=True)
    secteur_activite = models.CharField(_('Secteur d\'activité'), max_length=255, blank=True)

    # Confidentialité client
    est_confidentiel = models.BooleanField(
        _('Client confidentiel'),
        default=False,
        help_text=_('Si coché, le nom du client sera masqué sur le site public.')
    )

    # Type de réalisation
    type_realisation = models.CharField(
        _('Type de réalisation'),
        max_length=50,
        choices=TYPE_REALISATION_CHOICES,
        default='autre',
        help_text=_('Catégorie fonctionnelle de la réalisation.')
    )

    # Date & lieu & durée
    date_realisation = models.DateField(_('Date de réalisation'), null=True, blank=True, db_index=True)
    ville = models.CharField(_('Ville'), max_length=120, blank=True)
    province = models.CharField(_('Province'), max_length=120, blank=True)
    pays = models.CharField(_('Pays'), max_length=120, blank=True)
    duree = models.CharField(_('Durée'), max_length=120, blank=True, help_text=_('Durée du projet (ex: 3 mois).'))

    # Équipe
    chef_projet = models.CharField(_('Chef de projet'), max_length=255, blank=True)
    equipe_intervention = models.TextField(_('Équipe d\'intervention'), blank=True)

    # Relations vers services et produits
    services = models.ManyToManyField(
        'services.Service',
        related_name='realisations',
        blank=True,
        verbose_name=_('Services réalisés')
    )
    produits = models.ManyToManyField(
        'produits.Produit',
        related_name='realisations',
        blank=True,
        verbose_name=_('Produits utilisés')
    )

    # Résultats
    resultat_fr = models.TextField(_('Résultat (FR)'), blank=True)
    resultat_en = models.TextField(_('Résultat (EN)'), blank=True)

    # Témoignage associé (optionnel)
    temoignage = models.ForeignKey(
        'contact.Temoignage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='realisations',
        verbose_name=_('Témoignage associé'),
        help_text=_('Témoignage optionnel lié à cette réalisation.')
    )

    badge = models.CharField(_('Badge'), max_length=30, choices=BADGE_CHOICES, default='aucun')

    # Visibilité
    est_active = models.BooleanField(_('Est active'), default=True)
    mise_en_avant = models.BooleanField(_('Mise en avant'), default=False)
    ordre_affichage = models.PositiveIntegerField(_('Ordre d\'affichage'), default=0)

    # SEO
    meta_title_fr = models.CharField(_('Meta Title (FR)'), max_length=200, blank=True)
    meta_title_en = models.CharField(_('Meta Title (EN)'), max_length=200, blank=True)
    meta_description_fr = models.TextField(_('Meta Description (FR)'), blank=True)
    meta_description_en = models.TextField(_('Meta Description (EN)'), blank=True)

    class Meta:
        verbose_name = _('Réalisation')
        verbose_name_plural = _('Réalisations')
        ordering = ['-mise_en_avant', 'ordre_affichage', '-date_realisation']
        indexes = [
            models.Index(fields=['reference']),
            models.Index(fields=['slug_fr']),
            models.Index(fields=['slug_en']),
            models.Index(fields=['date_realisation']),
        ]

    def __str__(self):
        return self.nom_fr or self.reference

    def get_absolute_url(self):
        """
        URL canonique de la réalisation ; on utilise slug_fr pour la route publique FR.
        Adapter le nom de la route ('realisations:detail') si nécessaire.
        """
        return reverse('realisations:detail', kwargs={'slug': self.slug_fr})


class Galerie(TimestampedModel):
    TYPE_MEDIA_CHOICES = (
        ('image', _('Image')),
        ('video', _('Vidéo')),
    )

    realisation = models.ForeignKey(
        Realisation,
        on_delete=models.CASCADE,
        related_name='galeries',
        verbose_name=_('Réalisation')
    )

    type_media = models.CharField(_('Type de média'), max_length=20, choices=TYPE_MEDIA_CHOICES)

    titre_fr = models.CharField(_('Titre (FR)'), max_length=200, blank=True)
    titre_en = models.CharField(_('Titre (EN)'), max_length=200, blank=True)

    description_fr = models.TextField(_('Description (FR)'), blank=True)
    description_en = models.TextField(_('Description (EN)'), blank=True)

    image = models.ImageField(
        _('Image'),
        upload_to='realisations/images/',
        blank=True,
        null=True
    )
    video_url = models.URLField(
        _('Video URL'),
        blank=True,
        help_text=_('URL de la vidéo (YouTube ou Vimeo).')
    )

    ordre = models.PositiveIntegerField(_('Ordre'), default=0)
    est_principal = models.BooleanField(
        _('Est principal'),
        default=False,
        help_text=_('Indique si ce média est le média principal de la réalisation.')
    )

    class Meta:
        verbose_name = _('Galerie')
        verbose_name_plural = _('Galeries')
        ordering = ['ordre']
        indexes = [
            models.Index(fields=['realisation']),
        ]
        constraints = [
            UniqueConstraint(
                fields=['realisation'],
                condition=Q(est_principal=True),
                name='unique_principal_media_per_realisation'
            )
        ]

    def __str__(self):
        return self.titre_fr or self.titre_en or f"{self.realisation.reference} - {self.type_media}"
