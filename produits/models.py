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


class Produit(TimestampedModel):
    ETAT_CHOICES = (
        ('neuf', _('Neuf')),
        ('occasion', _('Occasion')),
        ('reconditionne', _('Reconditionné')),
    )

    BADGE_CHOICES = (
        ('nouveau', _('Nouveau')),
        ('promotion', _('Promotion')),
        ('populaire', _('Populaire')),
        ('meilleure_vente', _('Meilleure vente')),
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
        related_name='produits',
        verbose_name=_('Catégorie')
    )

    description_fr = models.TextField(_('Description (FR)'), blank=True)
    description_en = models.TextField(_('Description (EN)'), blank=True)

    image_principale = models.ImageField(
        _('Image principale'),
        upload_to='produits/images/',
        blank=True,
        null=True
    )

    brochure_pdf = models.FileField(
        _('Brochure (PDF)'),
        upload_to='produits/documents/',
        blank=True,
        null=True,
        help_text=_('Fichier PDF optionnel (fiche produit).')
    )

    video_presentation = models.URLField(
        _('Vidéo de présentation (YouTube/Vimeo)'),
        blank=True,
        help_text=_('URL de la vidéo de présentation (YouTube ou Vimeo).')
    )

    # Informations commerciales
    marque = models.CharField(_('Marque'), max_length=200, blank=True)
    modele = models.CharField(_('Modèle'), max_length=200, blank=True)

    etat = models.CharField(_('État'), max_length=20, choices=ETAT_CHOICES, default='neuf')

    prix = models.DecimalField(
        _('Prix'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    disponible = models.BooleanField(_('Disponible'), default=True)
    quantite_stock = models.PositiveIntegerField(
        _('Quantité en stock'),
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=_('Quantité disponible en stock (optionnel).')
    )

    # Relation ManyToMany vers Service (installation / options)
    services = models.ManyToManyField(
        'services.Service',
        related_name='produits',
        blank=True,
        verbose_name=_('Services associés')
    )

    # Personnalisation UI
    icone = models.CharField(
        _('Icône'),
        max_length=100,
        blank=True,
        help_text=_('Classe d\'icône (Bootstrap Icons / Font Awesome) pour représenter le produit.')
    )
    couleur = models.CharField(
        _('Couleur'),
        max_length=7,
        blank=True,
        validators=[HEX_COLOR_VALIDATOR],
        help_text=_('Couleur hexadécimale pour styliser la carte produit, ex. #0055AA.')
    )

    # Garantie et référence fournisseur (internes)
    garantie = models.CharField(_('Garantie'), max_length=100, blank=True, help_text=_('Durée de garantie, ex. 12 mois.'))
    reference_fournisseur = models.CharField(
        _('Référence fournisseur'),
        max_length=200,
        blank=True,
        help_text=_('Référence utilisée par le fournisseur (gestion interne).')
    )

    badge = models.CharField(_('Badge'), max_length=30, choices=BADGE_CHOICES, default='aucun')

    est_actif = models.BooleanField(_('Est actif'), default=True)
    mise_en_avant = models.BooleanField(_('Mise en avant'), default=False)
    ordre_affichage = models.PositiveIntegerField(_('Ordre d\'affichage'), default=0)
    date_publication = models.DateTimeField(_('Date de publication'), null=True, blank=True, db_index=True)

    meta_title_fr = models.CharField(_('Meta Title (FR)'), max_length=200, blank=True)
    meta_title_en = models.CharField(_('Meta Title (EN)'), max_length=200, blank=True)
    meta_description_fr = models.TextField(_('Meta Description (FR)'), blank=True)
    meta_description_en = models.TextField(_('Meta Description (EN)'), blank=True)

    class Meta:
        verbose_name = _('Produit')
        verbose_name_plural = _('Produits')
        ordering = ['-mise_en_avant', 'ordre_affichage', 'nom_fr']
        indexes = [
            models.Index(fields=['reference']),
            models.Index(fields=['slug_fr']),
            models.Index(fields=['slug_en']),
        ]

    def __str__(self):
        return f"{self.nom_fr} ({self.reference})"

    def get_absolute_url(self):
        """
        Retourne l'URL canonique d'un produit.
        Par convention on utilise slug_fr pour la route publique côté FR.
        Adapter le nom de la route ('produits:detail') si nécessaire dans urls.py.
        """
        return reverse('produits:detail', kwargs={'slug': self.slug_fr})


class ProduitMedia(TimestampedModel):
    TYPE_MEDIA_CHOICES = (
        ('image', _('Image')),
        ('video', _('Vidéo')),
        ('pdf', _('PDF')),
    )

    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        related_name='medias',
        verbose_name=_('Produit')
    )

    type_media = models.CharField(_('Type de média'), max_length=20, choices=TYPE_MEDIA_CHOICES)

    titre_fr = models.CharField(_('Titre (FR)'), max_length=200, blank=True)
    titre_en = models.CharField(_('Titre (EN)'), max_length=200, blank=True)

    image = models.ImageField(
        _('Image'),
        upload_to='produits/images/',
        blank=True,
        null=True
    )
    video_url = models.URLField(_('Video URL'), blank=True)
    document = models.FileField(
        _('Document'),
        upload_to='produits/documents/',
        blank=True,
        null=True
    )

    ordre = models.PositiveIntegerField(_('Ordre'), default=0)
    est_principal = models.BooleanField(
        _('Est principal'),
        default=False,
        help_text=_('Indique si ce média est l\'image/ressource principale du produit.')
    )

    class Meta:
        verbose_name = _('Média produit')
        verbose_name_plural = _('Médias produit')
        ordering = ['ordre']
        indexes = [
            models.Index(fields=['produit']),
        ]

    def __str__(self):
        return self.titre_fr or self.titre_en or f"{self.produit.reference} - {self.type_media}"


class DemandeProduit(TimestampedModel):
    TYPE_CLIENT_CHOICES = (
        ('particulier', _('Particulier')),
        ('entreprise', _('Entreprise')),
        ('ecole', _('École')),
        ('universite', _('Université')),
        ('organisation', _('Organisation')),
        ('administration', _('Administration publique')),
        ('ong', _('ONG')),
    )

    MODE_CONTACT_CHOICES = (
        ('whatsapp', _('WhatsApp')),
        ('telephone', _('Téléphone')),
        ('email', _('Email')),
    )

    STATUT_CHOICES = (
        ('nouvelle', _('Nouvelle')),
        ('contacte', _('Contacté')),
        ('confirmee', _('Confirmée')),
        ('livree', _('Livrée')),
        ('annulee', _('Annulée')),
    )

    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        related_name='demandes',
        verbose_name=_('Produit')
    )

    # Informations personnelles
    nom = models.CharField(_('Nom'), max_length=120)
    postnom = models.CharField(_('Postnom'), max_length=120, blank=True)
    prenom = models.CharField(_('Prénom'), max_length=120)
    telephone = models.CharField(_('Téléphone'), max_length=40)
    email = models.EmailField(_('Email'))

    # Adresse
    adresse = models.TextField(_('Adresse'), blank=True)
    ville = models.CharField(_('Ville'), max_length=120, blank=True)
    province = models.CharField(_('Province'), max_length=120, blank=True)
    pays = models.CharField(_('Pays'), max_length=120, blank=True)

    # Organisation / client
    type_client = models.CharField(
        _('Type client'),
        max_length=30,
        choices=TYPE_CLIENT_CHOICES,
        default='particulier'
    )
    nom_organisation = models.CharField(_('Nom organisation'), max_length=200, blank=True)
    responsable = models.CharField(_('Responsable'), max_length=200, blank=True)

    # Commande
    quantite = models.PositiveIntegerField(_('Quantité'), default=1, validators=[MinValueValidator(1)])

    # Installation
    demander_installation = models.BooleanField(_('Demander installation'), default=False)
    service_souhaite = models.ForeignKey(
        'services.Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='demandes_produits',
        verbose_name=_('Service souhaité'),
        help_text=_('Service d\'installation souhaité (optionnel).')
    )

    # Description
    commentaire_client = models.TextField(_('Commentaire client'), blank=True)

    mode_contact_prefere = models.CharField(
        _('Mode de contact préféré'),
        max_length=20,
        choices=MODE_CONTACT_CHOICES,
        default='whatsapp'
    )

    statut = models.CharField(_('Statut'), max_length=30, choices=STATUT_CHOICES, default='nouvelle')

    # Administration
    commentaire_admin = models.TextField(_('Commentaire admin'), blank=True)
    traite_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='demandes_produits_traitees',
        verbose_name=_('Traité par')
    )
    date_traitement = models.DateTimeField(_('Date de traitement'), null=True, blank=True)

    # PDF
    pdf_file = models.FileField(
        _('PDF récapitulatif'),
        upload_to='produits/documents/',
        blank=True,
        null=True,
        help_text=_('Fichier PDF généré pour récapitulatif.')
    )
    pdf_genere = models.BooleanField(_('PDF généré'), default=False)

    class Meta:
        verbose_name = _('Demande de produit')
        verbose_name_plural = _('Demandes de produit')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['produit']),
            models.Index(fields=['email']),
            models.Index(fields=['statut']),
        ]

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.produit.reference}"