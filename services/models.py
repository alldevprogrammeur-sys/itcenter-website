from django.db import models

# Create your models here.
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


HEX_COLOR_VALIDATOR = RegexValidator(
    regex=r'^#(?:[0-9a-fA-F]{3}){1,2}$',
    message=_('Entrez une couleur hexadécimale valide, ex. #RRGGBB.')
)


class TimestampedModel(models.Model):
    """
    Modèle abstrait fournissant created_at / updated_at.
    """
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Service(TimestampedModel):
    BADGE_CHOICES = (
        ('nouveau', _('Nouveau')),
        ('populaire', _('Populaire')),
        ('recommande', _('Recommandé')),
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
        related_name='services',
        verbose_name=_('Catégorie')
    )

    description_fr = models.TextField(_('Description (FR)'), blank=True)
    description_en = models.TextField(_('Description (EN)'), blank=True)

    image_principale = models.ImageField(
        _('Image principale'),
        upload_to='services/images/',
        blank=True,
        null=True
    )

    brochure_pdf = models.FileField(
        _('Brochure (PDF)'),
        upload_to='services/brochures/',
        blank=True,
        null=True,
        help_text=_('Fichier PDF optionnel de présentation.')
    )

    video_presentation = models.URLField(
        _('Vidéo de présentation (YouTube/Vimeo)'),
        blank=True,
        help_text=_('URL de la vidéo de présentation (YouTube ou Vimeo).')
    )

    prix_sur_devis = models.BooleanField(_('Prix sur devis'), default=True)

    inclus_fr = models.TextField(_('Inclus (FR)'), blank=True)
    inclus_en = models.TextField(_('Inclus (EN)'), blank=True)

    public_cible_fr = models.TextField(_('Public concerné (FR)'), blank=True)
    public_cible_en = models.TextField(_('Public concerné (EN)'), blank=True)

    badge = models.CharField(_('Badge'), max_length=30, choices=BADGE_CHOICES, default='aucun')

    est_active = models.BooleanField(_('Est active'), default=True)
    mise_en_avant = models.BooleanField(_('Mise en avant'), default=False)
    ordre_affichage = models.PositiveIntegerField(_('Ordre d\'affichage'), default=0)
    date_publication = models.DateTimeField(_('Date de publication'), null=True, blank=True, db_index=True)

    meta_title_fr = models.CharField(_('Meta Title (FR)'), max_length=200, blank=True)
    meta_title_en = models.CharField(_('Meta Title (EN)'), max_length=200, blank=True)
    meta_description_fr = models.TextField(_('Meta Description (FR)'), blank=True)
    meta_description_en = models.TextField(_('Meta Description (EN)'), blank=True)

    # UI customization
    icone = models.CharField(
        _('Icône'),
        max_length=100,
        blank=True,
        help_text=_('Classe d\'icône (ex: Bootstrap Icons ou Font Awesome) utilisée pour représenter le service.')
    )
    couleur = models.CharField(
        _('Couleur'),
        max_length=7,
        blank=True,
        validators=[HEX_COLOR_VALIDATOR],
        help_text=_('Couleur hexadécimale utilisée pour styliser la carte du service, ex. #0055AA.')
    )

    class Meta:
        verbose_name = _('Service')
        verbose_name_plural = _('Services')
        ordering = ['-mise_en_avant', 'ordre_affichage', 'nom_fr']
        indexes = [
            models.Index(fields=['reference']),
            models.Index(fields=['slug_fr']),
            models.Index(fields=['slug_en']),
            models.Index(fields=['date_publication']),
        ]

    def __str__(self):
        return f"{self.nom_fr} ({self.reference})"

    def get_absolute_url(self):
        """
        Retourne l'URL canonique d'un service.
        Par convention on utilise slug_fr pour la route publique côté FR.
        Adapter le nom de la route ('services:detail') si nécessaire dans urls.py.
        """
        return reverse('services:detail', kwargs={'slug': self.slug_fr})


class DemandeService(TimestampedModel):
    TYPE_CLIENT_CHOICES = (
        ('particulier', _('Particulier')),
        ('entreprise', _('Entreprise')),
        ('ecole', _('École')),
        ('universite', _('Université')),
        ('organisation', _('Organisation')),
        ('administration', _('Administration publique')),
        ('ong', _('ONG')),
    )

    NIVEAU_URGENCE_CHOICES = (
        ('faible', _('Faible')),
        ('normal', _('Normal')),
        ('urgent', _('Urgent')),
    )

    MODE_CONTACT_CHOICES = (
        ('whatsapp', _('WhatsApp')),
        ('telephone', _('Téléphone')),
        ('email', _('Email')),
    )

    STATUT_CHOICES = (
        ('nouvelle', _('Nouvelle')),
        ('en_etude', _('En étude')),
        ('contacte', _('Contacté')),
        ('devis_envoye', _('Devis envoyé')),
        ('acceptee', _('Acceptée')),
        ('refusee', _('Refusée')),
        ('terminee', _('Terminée')),
    )

    SOURCE_DEMANDE_CHOICES = (
        ('site_web', _('Site Web')),
        ('whatsapp', _('WhatsApp')),
        ('telephone', _('Téléphone')),
        ('facebook', _('Facebook')),
        ('linkedin', _('LinkedIn')),
        ('reference', _('Référence')),
        ('autre', _('Autre')),
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='demandes',
        verbose_name=_('Service')
    )

    # Informations personnelles
    nom = models.CharField(_('Nom'), max_length=120)
    postnom = models.CharField(_('Postnom'), max_length=120, blank=True)
    prenom = models.CharField(_('Prénom'), max_length=120)
    telephone = models.CharField(_('Téléphone'), max_length=40)  # rendu obligatoire
    email = models.EmailField(_('Email'))

    adresse = models.TextField(_('Adresse'), blank=True)
    ville = models.CharField(_('Ville'), max_length=120, blank=True)
    province = models.CharField(_('Province'), max_length=120, blank=True)
    pays = models.CharField(_('Pays'), max_length=120, blank=True)

    type_client = models.CharField(
        _('Type de client'),
        max_length=30,
        choices=TYPE_CLIENT_CHOICES,
        default='particulier'
    )

    nom_organisation = models.CharField(_('Nom organisation'), max_length=200, blank=True)
    responsable = models.CharField(_('Responsable'), max_length=200, blank=True)
    fonction = models.CharField(_('Fonction'), max_length=200, blank=True)
    nombre_personnes = models.PositiveIntegerField(
        _('Nombre de personnes'),
        null=True,
        blank=True,
        validators=[MinValueValidator(1)]
    )

    description_besoin = models.TextField(_('Description du besoin'))  # rendu obligatoire

    adresse_intervention = models.TextField(_('Adresse d\'intervention'), blank=True)
    ville_intervention = models.CharField(_('Ville d\'intervention'), max_length=120, blank=True)
    province_intervention = models.CharField(_('Province d\'intervention'), max_length=120, blank=True)
    pays_intervention = models.CharField(_('Pays d\'intervention'), max_length=120, blank=True)

    date_souhaitee = models.DateField(_('Date souhaitée'), null=True, blank=True)

    niveau_urgence = models.CharField(
        _('Niveau d\'urgence'),
        max_length=20,
        choices=NIVEAU_URGENCE_CHOICES,
        default='normal'
    )

    mode_contact_prefere = models.CharField(
        _('Mode de contact préféré'),
        max_length=20,
        choices=MODE_CONTACT_CHOICES,
        default='whatsapp'
    )

    source_demande = models.CharField(
        _('Source de la demande'),
        max_length=30,
        choices=SOURCE_DEMANDE_CHOICES,
        default='site_web',
        help_text=_('Origine identifiée de la demande.')
    )

    piece_jointe = models.FileField(
        _('Pièce jointe'),
        upload_to='services/documents/',
        blank=True,
        null=True
    )

    # Traitement administratif
    statut = models.CharField(_('Statut'), max_length=30, choices=STATUT_CHOICES, default='nouvelle')
    commentaire_admin = models.TextField(_('Commentaire admin'), blank=True)

    traite_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='demandes_traitees',
        verbose_name=_('Traité par')
    )
    date_traitement = models.DateTimeField(_('Date de traitement'), null=True, blank=True)

    # PDF récapitulatif
    pdf_file = models.FileField(
        _('PDF récapitulatif'),
        upload_to='services/documents/',
        blank=True,
        null=True,
        help_text=_('Fichier PDF généré pour récapitulatif.')
    )
    pdf_genere = models.BooleanField(_('PDF généré'), default=False)

    class Meta:
        verbose_name = _('Demande de service')
        verbose_name_plural = _('Demandes de service')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['service']),
            models.Index(fields=['email']),
            models.Index(fields=['statut']),
        ]

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.service.reference}"
