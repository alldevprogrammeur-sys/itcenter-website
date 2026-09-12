from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
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


class ParametreSite(TimestampedModel):
    """
    Singleton : configuration générale du site.
    Empêche la création de plusieurs instances via l'override de save().
    """
    LANG_CHOICES = (
        ('fr', 'Français'),
        ('en', 'Anglais'),
    )

    site_name = models.CharField(_('Nom du site'), max_length=200, db_index=True)
    logo = models.ImageField(_('Logo'), upload_to='site/', blank=True, null=True)
    favicon = models.ImageField(_('Favicon'), upload_to='site/', blank=True, null=True)
    adresse = models.TextField(_('Adresse'), blank=True)
    telephone_1 = models.CharField(_('Téléphone 1'), max_length=40, blank=True)
    telephone_2 = models.CharField(_('Téléphone 2'), max_length=40, blank=True)
    telephone_3 = models.CharField(_('Téléphone 3'), max_length=40, blank=True)
    email_principal = models.EmailField(_('Email principal'), blank=True)
    email_secondaire = models.EmailField(_('Email secondaire'), blank=True)
    couleur_primaire = models.CharField(
        _('Couleur principale'),
        max_length=7,
        validators=[HEX_COLOR_VALIDATOR],
        blank=True
    )
    couleur_secondaire = models.CharField(
        _('Couleur secondaire'),
        max_length=7,
        validators=[HEX_COLOR_VALIDATOR],
        blank=True
    )
    google_maps_embed = models.TextField(_('Google Maps (embed)'), blank=True)

    facebook_url = models.URLField(_('Facebook (URL)'), blank=True)
    linkedin_url = models.URLField(_('LinkedIn (URL)'), blank=True)
    youtube_url = models.URLField(_('YouTube (URL)'), blank=True)
    instagram_url = models.URLField(_('Instagram (URL)'), blank=True)
    telegram_url = models.URLField(_('Telegram (URL)'), blank=True)
    whatsapp = models.CharField(_('WhatsApp (numéro ou lien)'), max_length=200, blank=True)
    x_url = models.URLField(_('X / Twitter (URL)'), blank=True)
    tiktok_url = models.URLField(_('TikTok (URL)'), blank=True)
    github_url = models.URLField(_('GitHub (URL)'), blank=True)

    seo_meta_title = models.CharField(_('SEO - Meta Title'), max_length=200, blank=True)
    seo_meta_description = models.TextField(_('SEO - Meta Description'), blank=True)

    langue_par_defaut = models.CharField(
        _('Langue par défaut'),
        max_length=2,
        choices=LANG_CHOICES,
        default='fr'
    )

    copyright = models.CharField(_('Copyright'), max_length=250, blank=True)
    site_actif = models.BooleanField(_('Site actif'), default=True)

    class Meta:
        verbose_name = _('Paramètre du site')
        verbose_name_plural = _('Paramètres du site')
        ordering = ['-updated_at']

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        """
        Empêche la création d'une seconde instance.
        Permet la modification de l'instance existante.
        """
        if not self.pk and ParametreSite.objects.exists():
            raise ValidationError(_('Une seule configuration ParametreSite est autorisée.'))
        return super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        """
        Retourne l'instance unique si elle existe, sinon None.
        Utilitaire pratique pour le code appelant.
        """
        return cls.objects.first()


class Categorie(TimestampedModel):
    nom_fr = models.CharField(_('Nom (FR)'), max_length=150, db_index=True)
    nom_en = models.CharField(_('Nom (EN)'), max_length=150, blank=True)
    slug = models.SlugField(_('Slug'), max_length=160, unique=True)
    description_fr = models.TextField(_('Description (FR)'), blank=True)
    description_en = models.TextField(_('Description (EN)'), blank=True)
    image = models.ImageField(_('Image'), upload_to='categories/', blank=True, null=True)
    actif = models.BooleanField(_('Actif'), default=True)

    class Meta:
        verbose_name = _('Catégorie')
        verbose_name_plural = _('Catégories')
        ordering = ['nom_fr']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['nom_fr']),
        ]

    def __str__(self):
        return self.nom_fr or self.nom_en or self.slug


class Departement(TimestampedModel):
    nom_fr = models.CharField(_('Nom (FR)'), max_length=150, db_index=True)
    nom_en = models.CharField(_('Nom (EN)'), max_length=150, blank=True)
    slug = models.SlugField(_('Slug'), max_length=160, unique=True)
    description = models.TextField(_('Description'), blank=True)
    image = models.ImageField(_('Image'), upload_to='departements/', blank=True, null=True)

    class Meta:
        verbose_name = _('Département')
        verbose_name_plural = _('Départements')
        ordering = ['nom_fr']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['nom_fr']),
        ]

    def __str__(self):
        return self.nom_fr


class Poste(TimestampedModel):
    nom_fr = models.CharField(_('Nom (FR)'), max_length=150, db_index=True)
    nom_en = models.CharField(_('Nom (EN)'), max_length=150, blank=True)
    slug = models.SlugField(_('Slug'), max_length=160, unique=True)
    description = models.TextField(_('Description'), blank=True)
    image = models.ImageField(_('Image'), upload_to='postes/', blank=True, null=True)

    class Meta:
        verbose_name = _('Poste')
        verbose_name_plural = _('Postes')
        ordering = ['nom_fr']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['nom_fr']),
        ]

    def __str__(self):
        return self.nom_fr


class Competence(TimestampedModel):
    """
    Compétence normalisée. Créée en Admin. Liée à Membre via M2M.
    """
    nom_fr = models.CharField(_('Nom (FR)'), max_length=120, db_index=True)
    nom_en = models.CharField(_('Nom (EN)'), max_length=120, blank=True)
    slug = models.SlugField(_('Slug'), max_length=140, unique=True)
    description = models.TextField(_('Description'), blank=True)

    class Meta:
        verbose_name = _('Compétence')
        verbose_name_plural = _('Compétences')
        ordering = ['nom_fr']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['nom_fr']),
        ]

    def __str__(self):
        return self.nom_fr or self.nom_en or self.slug

class APropos(TimestampedModel):
    """
    Contenu institutionnel principal de la section
    « À propos de IT CENTER ».

    Singleton : une seule instance autorisée.
    """

    # Titres
    titre_fr = models.CharField(
        _('Titre (FR)'),
        max_length=200,
        blank=True,
        help_text=_('Titre en français.')
    )
    titre_en = models.CharField(
        _('Titre (EN)'),
        max_length=200,
        blank=True,
        help_text=_('Titre en anglais.')
    )

    # Accroche
    accroche_fr = models.TextField(_('Accroche (FR)'), blank=True)
    accroche_en = models.TextField(_('Accroche (EN)'), blank=True)

    # Description
    description_fr = models.TextField(_('Description (FR)'), blank=True)
    description_en = models.TextField(_('Description (EN)'), blank=True)

    # Mission / Vision
    mission_fr = models.TextField(_('Mission (FR)'), blank=True)
    mission_en = models.TextField(_('Mission (EN)'), blank=True)

    vision_fr = models.TextField(_('Vision (FR)'), blank=True)
    vision_en = models.TextField(_('Vision (EN)'), blank=True)

    # Illustration
    image = models.ImageField(
        _('Photo de IT CENTER'),
        upload_to='a_propos/',
        blank=True,
        null=True
    )

    # Bouton
    bouton_texte_fr = models.CharField(
        _('Texte du bouton (FR)'),
        max_length=100,
        blank=True
    )
    bouton_texte_en = models.CharField(
        _('Texte du bouton (EN)'),
        max_length=100,
        blank=True
    )
    bouton_url = models.CharField(
        _('URL du bouton'),
        max_length=255,
        blank=True
    )

    actif = models.BooleanField(_('Actif'), default=True)

    class Meta:
        verbose_name = _('À propos')
        verbose_name_plural = _('À propos')
        ordering = ['-updated_at']

    def __str__(self):
        # Prefer French title, fallback to English, then a generic label
        return self.titre_fr or self.titre_en or _('À propos')

    def save(self, *args, **kwargs):
        """
        Empêche la création de plusieurs contenus principaux « À propos ».
        """
        if not self.pk and APropos.objects.exists():
            raise ValidationError(
                _('Une seule configuration À propos est autorisée.')
            )
        return super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        """
        Retourne l'unique contenu À propos s'il existe.
        """
        return cls.objects.first()


class Valeur(TimestampedModel):
    """
    Valeur fondamentale de IT CENTER.

    Les valeurs sont gérées séparément afin de permettre
    un affichage dynamique sous forme de cartes/blocs.
    """

    apropos = models.ForeignKey(
        APropos,
        on_delete=models.CASCADE,
        related_name='valeurs',
        verbose_name=_('À propos')
    )

    # Titres bilingues
    titre_fr = models.CharField(
        _('Titre (FR)'),
        max_length=150,
        blank=True
    )
    titre_en = models.CharField(
        _('Titre (EN)'),
        max_length=150,
        blank=True
    )

    # Descriptions bilingues
    description_fr = models.TextField(
        _('Description (FR)'),
        blank=True
    )
    description_en = models.TextField(
        _('Description (EN)'),
        blank=True
    )

    icone = models.CharField(
        _('Icône'),
        max_length=100,
        blank=True,
        help_text=_(
            'Nom ou classe CSS de l’icône utilisée sur le site.'
        )
    )

    ordre = models.PositiveIntegerField(
        _('Ordre d’affichage'),
        default=0
    )

    actif = models.BooleanField(
        _('Actif'),
        default=True
    )

    class Meta:
        verbose_name = _('Valeur')
        verbose_name_plural = _('Valeurs')
        ordering = ['ordre', 'titre_fr']
        indexes = [
            models.Index(fields=['ordre']),
            models.Index(fields=['actif']),
        ]

    def __str__(self):
        return self.titre_fr or self.titre_en or ''


class Membre(TimestampedModel):
    nom_complet = models.CharField(_('Nom complet'), max_length=200, db_index=True)
    slug = models.SlugField(_('Slug'), max_length=220, unique=True)
    departement = models.ForeignKey(
        Departement,
        on_delete=models.PROTECT,
        related_name='membres',
        verbose_name=_('Département')
    )
    poste = models.ForeignKey(
        Poste,
        on_delete=models.PROTECT,
        related_name='membres',
        verbose_name=_('Poste')
    )
    photo = models.ImageField(_('Photo'), upload_to='membres/', blank=True, null=True)

    presentation_fr = models.TextField(_('Présentation (FR)'), blank=True)
    presentation_en = models.TextField(_('Présentation (EN)'), blank=True)
    biographie_fr = models.TextField(_('Biographie (FR)'), blank=True)
    biographie_en = models.TextField(_('Biographie (EN)'), blank=True)

    telephone_1 = models.CharField(_('Téléphone 1'), max_length=40, blank=True)
    telephone_2 = models.CharField(_('Téléphone 2'), max_length=40, blank=True)
    telephone_3 = models.CharField(_('Téléphone 3'), max_length=40, blank=True)

    email_principal = models.EmailField(_('Email principal'), blank=True)
    email_secondaire = models.EmailField(_('Email secondaire'), blank=True)

    competences = models.ManyToManyField(
        Competence,
        related_name='membres',
        blank=True,
        verbose_name=_('Compétences')
    )

    facebook_url = models.URLField(_('Facebook (URL)'), blank=True)
    linkedin_url = models.URLField(_('LinkedIn (URL)'), blank=True)
    youtube_url = models.URLField(_('YouTube (URL)'), blank=True)
    instagram_url = models.URLField(_('Instagram (URL)'), blank=True)
    telegram_url = models.URLField(_('Telegram (URL)'), blank=True)
    whatsapp = models.CharField(_('WhatsApp (numéro ou lien)'), max_length=200, blank=True)
    x_url = models.URLField(_('X / Twitter (URL)'), blank=True)
    tiktok_url = models.URLField(_('TikTok (URL)'), blank=True)
    github_url = models.URLField(_('GitHub (URL)'), blank=True)

    experience = models.TextField(_('Expérience'), blank=True)
    ordre_affichage = models.PositiveIntegerField(_('Ordre d\'affichage'), default=0)
    mise_en_avant = models.BooleanField(_('Mise en avant'), default=False)
    afficher_sur_site = models.BooleanField(_('Afficher sur le site'), default=True)
    statut_formateur = models.BooleanField(_('Statut formateur'), default=False)

    seo_title = models.CharField(_('SEO - Titre'), max_length=200, blank=True)
    seo_description = models.TextField(_('SEO - Description'), blank=True)

    class Meta:
        verbose_name = _('Membre')
        verbose_name_plural = _('Membres')
        ordering = ['-mise_en_avant', 'ordre_affichage', 'nom_complet']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['nom_complet']),
        ]

    def __str__(self):
        return self.nom_complet

class DomaineExpertise(TimestampedModel):
    """
    Domaine d'expertise présenté dans l'Accueil (Section 'Domaines d'expertise').

    Stockage bilingue (FR / EN) pour titre et description.
    """
    titre_fr = models.CharField(
        _('Titre (FR)'),
        max_length=200,
        blank=True
    )
    titre_en = models.CharField(
        _('Titre (EN)'),
        max_length=200,
        blank=True
    )

    description_fr = models.TextField(
        _('Description (FR)'),
        blank=True
    )
    description_en = models.TextField(
        _('Description (EN)'),
        blank=True
    )

    icone = models.CharField(
        _('Icône'),
        max_length=100,
        blank=True,
        help_text=_('Nom ou classe CSS de l’icône utilisée sur le site.')
    )

    image = models.ImageField(
        _('Image'),
        upload_to='domaines_expertise/',
        blank=True,
        null=True
    )

    ordre = models.PositiveIntegerField(
        _('Ordre d’affichage'),
        default=0
    )

    actif = models.BooleanField(
        _('Actif'),
        default=True
    )

    class Meta:
        verbose_name = _('Domaine d\'expertise')
        verbose_name_plural = _('Domaines d\'expertise')
        ordering = ['ordre', 'titre_fr']
        indexes = [
            models.Index(fields=['ordre']),
            models.Index(fields=['actif']),
        ]

    def __str__(self):
        # Priorité au titre français
        return self.titre_fr or self.titre_en or ''
