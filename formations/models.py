from django.db import models

# Create your models here.
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
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


class Formation(TimestampedModel):
    TYPE_FORMATION_CHOICES = (
        ('presentiel', _('Présentiel / Local')),
        ('en_ligne', _('En ligne')),
    )

    BADGE_CHOICES = (
        ('nouvelle', _('Nouvelle')),
        ('populaire', _('Populaire')),
        ('tres_demandee', _('Très demandée')),
        ('certification', _('Certification')),
        ('aucun', _('Aucun')),
    )

    CERTIFICAT_TYPE_CHOICES = (
        ('attestation', _('Attestation')),
        ('certificat', _('Certificat')),
        ('diplome_interne', _('Diplôme interne')),
    )

    reference = models.CharField(_('Référence'), max_length=100, unique=True, db_index=True)
    nom_fr = models.CharField(_('Nom (FR)'), max_length=255, db_index=True)
    nom_en = models.CharField(_('Nom (EN)'), max_length=255, blank=True)
    slug_fr = models.SlugField(_('Slug (FR)'), max_length=255, unique=True, db_index=True)
    slug_en = models.SlugField(_('Slug (EN)'), max_length=255, unique=True, db_index=True)

    # Relation vers core.Categorie
    categorie = models.ForeignKey(
        'core.Categorie',
        on_delete=models.PROTECT,
        related_name='formations',
        verbose_name=_('Catégorie')
    )

    type_formation = models.CharField(
        _('Type de formation'),
        max_length=20,
        choices=TYPE_FORMATION_CHOICES,
        default='presentiel'
    )

    # Présentation
    description_fr = models.TextField(_('Description (FR)'), blank=True)
    description_en = models.TextField(_('Description (EN)'), blank=True)
    image_principale = models.ImageField(
        _('Image principale'),
        upload_to='formations/images/',
        blank=True,
        null=True
    )
    brochure_pdf = models.FileField(
        _('Brochure (PDF)'),
        upload_to='formations/brochures/',
        blank=True,
        null=True,
        help_text=_('Fichier PDF optionnel de présentation.')
    )
    video_presentation = models.URLField(
        _('Vidéo de présentation (YouTube/Vimeo)'),
        blank=True,
        help_text=_('URL de la vidéo de présentation (YouTube ou Vimeo).')
    )

    # Informations pédagogiques
    niveau = models.CharField(_('Niveau'), max_length=120, blank=True)
    duree_valeur = models.PositiveIntegerField(
        _('Durée (valeur)'),
        validators=[MinValueValidator(1)],
        null=True,
        blank=True,
        help_text=_('Valeur numérique de la durée (ex: 5).')
    )
    duree_unite = models.CharField(_('Durée (unité)'), max_length=50, blank=True,
                                   help_text=_('Unité (ex: jours, semaines, mois).'))
    duree_heures = models.PositiveIntegerField(
        _('Durée (heures)'),
        validators=[MinValueValidator(0)],
        default=0
    )
    prix = models.DecimalField(
        _('Prix'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    devise = models.CharField(_('Devise'), max_length=10, blank=True,
                              help_text=_('Peut être héritée des paramètres du site.'))
    places_max = models.PositiveIntegerField(
        _('Places max'),
        validators=[MinValueValidator(1)],
        default=1
    )

    # Formateur (ForeignKey -> core.Membre)
    formateur = models.ForeignKey(
        'core.Membre',
        on_delete=models.PROTECT,
        related_name='formations',
        verbose_name=_('Formateur')
    )

    # Compétences acquises (ManyToMany -> core.Competence)
    competences = models.ManyToManyField(
        'core.Competence',
        related_name='formations',
        blank=True,
        verbose_name=_('Compétences acquises')
    )

    # Prérequis / Objectifs / Débouchés / Public cible / Matériel fourni
    prerequis_fr = models.TextField(_('Prérequis (FR)'), blank=True)
    prerequis_en = models.TextField(_('Prérequis (EN)'), blank=True)
    objectif_fr = models.TextField(_('Objectif (FR)'), blank=True)
    objectif_en = models.TextField(_('Objectif (EN)'), blank=True)
    debouches_fr = models.TextField(_('Débouchés (FR)'), blank=True)
    debouches_en = models.TextField(_('Débouchés (EN)'), blank=True)
    public_cible_fr = models.TextField(_('Public cible (FR)'), blank=True)
    public_cible_en = models.TextField(_('Public cible (EN)'), blank=True)
    materiel_fourni_fr = models.TextField(_('Matériel fourni (FR)'), blank=True)
    materiel_fourni_en = models.TextField(_('Matériel fourni (EN)'), blank=True)

    # Badge
    badge = models.CharField(_('Badge'), max_length=30, choices=BADGE_CHOICES, default='aucun')

    # Certificat
    certificat = models.BooleanField(_('Certificat'), default=False)
    type_certificat = models.CharField(
        _('Type de certificat'),
        max_length=30,
        choices=CERTIFICAT_TYPE_CHOICES,
        blank=True
    )

    # Visibilité
    est_active = models.BooleanField(_('Est active'), default=True)
    mise_en_avant = models.BooleanField(_('Mise en avant'), default=False)
    ordre_affichage = models.PositiveIntegerField(_('Ordre d\'affichage'), default=0)
    date_publication = models.DateTimeField(_('Date de publication'), null=True, blank=True)
    galerie_active = models.BooleanField(_('Galerie active'), default=False)

    # SEO
    meta_title_fr = models.CharField(_('Meta Title (FR)'), max_length=200, blank=True)
    meta_title_en = models.CharField(_('Meta Title (EN)'), max_length=200, blank=True)
    meta_description_fr = models.TextField(_('Meta Description (FR)'), blank=True)
    meta_description_en = models.TextField(_('Meta Description (EN)'), blank=True)

    class Meta:
        verbose_name = _('Formation')
        verbose_name_plural = _('Formations')
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
        Retourne l'URL canonique d'une formation.
        Par convention on utilise le slug_fr pour la route publique côté FR.
        L'implémentation du nom de route ('formations:detail') doit être définie
        dans urls.py ; adapter si nécessaire.
        """
        return reverse('formations:detail', kwargs={'slug': self.slug_fr})


class Inscription(TimestampedModel):
    MODE_FORMATION_CHOICES = (
        ('presentiel', _('Présentiel')),
        ('zoom', _('Zoom')),
        ('google_meet', _('Google Meet')),
    )

    TYPE_DEMANDE_CHOICES = (
        ('individuelle', _('Individuelle')),
        ('privee', _('Privée')),
        ('groupe', _('Groupe')),
        ('entreprise', _('Entreprise')),
    )

    STATUT_CHOICES = (
        ('en_attente', _('En attente')),
        ('contacte', _('Contacté')),
        ('confirme', _('Confirmé')),
        ('annule', _('Annulé')),
    )

    formation = models.ForeignKey(
        Formation,
        on_delete=models.CASCADE,
        related_name='inscriptions',
        verbose_name=_('Formation')
    )

    # Informations personnelles
    nom = models.CharField(_('Nom'), max_length=120)
    postnom = models.CharField(_('Postnom'), max_length=120, blank=True)
    prenom = models.CharField(_('Prénom'), max_length=120)
    sexe = models.CharField(
        _('Sexe'),
        max_length=20,
        choices=(
            ('masculin', _('Masculin')),
            ('feminin', _('Féminin')),
            ('autre', _('Autre')),
        ),
        blank=True
    )
    date_naissance = models.DateField(_('Date de naissance'), null=True, blank=True)

    # Coordonnées
    email = models.EmailField(_('Email'))  # obligatoire conservée
    telephone = models.CharField(_('Téléphone'), max_length=40, blank=True)

    # Adresse
    pays = models.CharField(_('Pays'), max_length=120, blank=True)
    province = models.CharField(_('Province'), max_length=120, blank=True)
    ville = models.CharField(_('Ville'), max_length=120, blank=True)
    adresse_complete = models.TextField(_('Adresse complète'), blank=True)

    # Mode & type de la demande
    mode_formation = models.CharField(
        _('Mode de formation'),
        max_length=20,
        choices=MODE_FORMATION_CHOICES,
        default='presentiel'
    )
    type_demande = models.CharField(
        _('Type de demande'),
        max_length=20,
        choices=TYPE_DEMANDE_CHOICES,
        default='individuelle'
    )

    # Informations complémentaires
    nom_entreprise = models.CharField(_('Nom entreprise'), max_length=200, blank=True)
    nom_groupe = models.CharField(_('Nom groupe'), max_length=200, blank=True)
    nombre_participants = models.PositiveIntegerField(_('Nombre participants'), null=True, blank=True)

    # Commentaires
    message = models.TextField(_('Message'), blank=True)

    # Statut
    statut = models.CharField(_('Statut'), max_length=20, choices=STATUT_CHOICES, default='en_attente')

    # PDF récapitulatif (prévu pour génération + envoi via WhatsApp)
    pdf_file = models.FileField(
        _('PDF récapitulatif'),
        upload_to='formations/documents/',
        blank=True,
        null=True,
        help_text=_('Fichier PDF généré et envoyé éventuellement via WhatsApp.')
    )
    pdf_genere = models.BooleanField(_('PDF généré'), default=False)

    class Meta:
        verbose_name = _('Inscription')
        verbose_name_plural = _('Inscriptions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['formation']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.formation.reference}"


class FormationMedia(TimestampedModel):
    TYPE_MEDIA_CHOICES = (
        ('image', _('Image')),
        ('video', _('Vidéo')),
        ('document', _('Document')),
    )

    formation = models.ForeignKey(
        Formation,
        on_delete=models.CASCADE,
        related_name='medias',
        verbose_name=_('Formation')
    )

    type_media = models.CharField(_('Type de média'), max_length=20, choices=TYPE_MEDIA_CHOICES)

    titre_fr = models.CharField(_('Titre (FR)'), max_length=200, blank=True)
    titre_en = models.CharField(_('Titre (EN)'), max_length=200, blank=True)
    description_fr = models.TextField(_('Description (FR)'), blank=True)
    description_en = models.TextField(_('Description (EN)'), blank=True)

    image = models.ImageField(
        _('Image'),
        upload_to='formations/images/',
        blank=True,
        null=True
    )
    document = models.FileField(
        _('Document'),
        upload_to='formations/documents/',
        blank=True,
        null=True
    )
    video_url = models.URLField(_('Video URL'), blank=True)

    ordre_affichage = models.PositiveIntegerField(_('Ordre d\'affichage'), default=0)
    est_active = models.BooleanField(_('Est active'), default=True)

    class Meta:
        verbose_name = _('Média de formation')
        verbose_name_plural = _('Médias de formation')
        ordering = ['ordre_affichage']
        indexes = [
            models.Index(fields=['formation']),
        ]

    def __str__(self):
        return self.titre_fr or self.titre_en or f"{self.formation.reference} - {self.type_media}"