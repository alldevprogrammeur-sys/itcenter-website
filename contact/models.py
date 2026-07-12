from django.db import models

# Create your models here.
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


PHONE_REGEX = RegexValidator(
    regex=r'^[\d\+\-\.\(\)\/\s]{4,30}$',
    message=_('Numéro de téléphone invalide. Autorisé: chiffres, +, -, ., /, espaces, parenthèses.')
)


class TimestampedModel(models.Model):
    """
    Modèle abstrait fournissant created_at / updated_at.
    """
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Membre(TimestampedModel):
    reference = models.CharField(_('Référence'), max_length=100, unique=True, db_index=True)
    nom = models.CharField(_('Nom'), max_length=120, db_index=True)
    postnom = models.CharField(_('Postnom'), max_length=120, blank=True)
    prenom = models.CharField(_('Prénom'), max_length=120, blank=True)

    photo = models.ImageField(
        _('Photo'),
        upload_to='membres/',
        blank=True,
        null=True
    )

    # Poste administrable depuis core
    poste = models.ForeignKey(
        "core.Poste",
        on_delete=models.PROTECT,
        related_name="contact_membres",
        verbose_name=_('Poste')
    )

    # Fonction détaillée (affichée sur le site)
    fonction_fr = models.CharField(_('Fonction (FR)'), max_length=200, blank=True)
    fonction_en = models.CharField(_('Fonction (EN)'), max_length=200, blank=True)

    biographie_fr = models.TextField(_('Biographie (FR)'), blank=True)
    biographie_en = models.TextField(_('Biographie (EN)'), blank=True)

    telephone = models.CharField(_('Téléphone'), max_length=30, validators=[PHONE_REGEX], blank=True, db_index=True)
    email = models.EmailField(_('Email'), blank=True, db_index=True)

    facebook = models.URLField(_('Facebook (URL)'), blank=True)
    linkedin = models.URLField(_('LinkedIn (URL)'), blank=True)
    github = models.URLField(_('GitHub (URL)'), blank=True)
    x_twitter = models.URLField(_('X / Twitter (URL)'), blank=True)
    instagram = models.URLField(_('Instagram (URL)'), blank=True)

    ordre_affichage = models.PositiveIntegerField(_('Ordre d\'affichage'), default=0)
    date_entree = models.DateField(_('Date d\'entrée'), null=True, blank=True, help_text=_('Date d\'entrée dans l\'organisation (optionnel).'))
    est_fondateur = models.BooleanField(_('Est fondateur'), default=False)
    est_actif = models.BooleanField(_('Est actif'), default=True)
    mise_en_avant = models.BooleanField(_('Mise en avant'), default=False)

    class Meta:
        verbose_name = _('Membre')
        verbose_name_plural = _('Membres')
        ordering = ['-mise_en_avant', 'ordre_affichage', 'nom']
        indexes = [
            models.Index(fields=['reference']),
            models.Index(fields=['nom']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.get_full_name() or self.reference

    def get_full_name(self):
        """
        Retourne le nom complet au format: "nom postnom prenom"
        """
        parts = [self.nom, self.postnom, self.prenom]
        return ' '.join([p for p in parts if p]).strip()


class Temoignage(TimestampedModel):
    NOTE_CHOICES = [(i, f"{i} ★") for i in range(1, 6)]

    ORIGINE_CHOICES = (
        ('formation', _('Formation')),
        ('service', _('Service')),
        ('produit', _('Produit')),
        ('realisation', _('Réalisation')),
        ('autre', _('Autre')),
    )

    nom = models.CharField(_('Nom'), max_length=120, db_index=True)
    postnom = models.CharField(_('Postnom'), max_length=120, blank=True)
    prenom = models.CharField(_('Prénom'), max_length=120, blank=True)

    photo = models.ImageField(_('Photo'), upload_to='temoignages/', blank=True, null=True)

    fonction_fr = models.CharField(_('Fonction (FR)'), max_length=200, blank=True)
    fonction_en = models.CharField(_('Fonction (EN)'), max_length=200, blank=True)

    entreprise = models.CharField(_('Entreprise'), max_length=255, blank=True, db_index=True)

    message_fr = models.TextField(_('Message (FR)'), blank=True)
    message_en = models.TextField(_('Message (EN)'), blank=True)

    note = models.IntegerField(
        _('Note'),
        choices=NOTE_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text=_('Note de 1 à 5 étoiles.')
    )

    origine = models.CharField(_('Origine du témoignage'), max_length=30, choices=ORIGINE_CHOICES, default='autre', db_index=True)

    # Relations optionnelles vers d'autres entités
    formation = models.ForeignKey(
        'formations.Formation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='temoignages',
        verbose_name=_('Formation'),
        help_text=_('Optionnel : lien vers une formation si applicable.')
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='temoignages',
        verbose_name=_('Service'),
        help_text=_('Optionnel : lien vers un service si applicable.')
    )
    produit = models.ForeignKey(
        'produits.Produit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='temoignages',
        verbose_name=_('Produit'),
        help_text=_('Optionnel : lien vers un produit si applicable.')
    )
    realisation = models.ForeignKey(
        'realisations.Realisation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='temoignages',
        verbose_name=_('Réalisation'),
        help_text=_('Optionnel : lien vers une réalisation si applicable.')
    )

    est_valide = models.BooleanField(_('Est validé'), default=False, help_text=_('Coché si le témoignage a été vérifié et approuvé.'))
    mise_en_avant = models.BooleanField(_('Mise en avant'), default=False)

    class Meta:
        verbose_name = _('Témoignage')
        verbose_name_plural = _('Témoignages')
        ordering = ['-mise_en_avant', '-created_at']
        indexes = [
            models.Index(fields=['entreprise']),
            models.Index(fields=['origine']),
            models.Index(fields=['note']),
        ]

    def __str__(self):
        name = self.get_full_name()
        return f"{name} - {self.entreprise}" if self.entreprise else name or f"Témoignage {self.pk}"

    def get_full_name(self):
        """
        Retourne le nom complet au format: "nom postnom prenom"
        """
        parts = [self.nom, self.postnom, self.prenom]
        return ' '.join([p for p in parts if p]).strip()


class Partenaire(TimestampedModel):
    TYPE_PARTENAIRE_CHOICES = (
        ('entreprise', _('Entreprise')),
        ('organisation', _('Organisation')),
        ('universite', _('Université')),
        ('ecole', _('École')),
        ('institution', _('Institution')),
        ('partenaire_technique', _('Partenaire technique')),
        ('partenaire_commercial', _('Partenaire commercial')),
        ('personne', _('Personne')),
        ('autre', _('Autre')),
    )

    reference = models.CharField(_('Référence'), max_length=100, unique=True, db_index=True)
    nom = models.CharField(_('Nom'), max_length=255, db_index=True)

    logo = models.ImageField(_('Logo'), upload_to='partenaires/', blank=True, null=True)

    description_fr = models.TextField(_('Description (FR)'), blank=True)
    description_en = models.TextField(_('Description (EN)'), blank=True)

    type = models.CharField(_('Type'), max_length=30, choices=TYPE_PARTENAIRE_CHOICES, default='entreprise')

    site_web = models.URLField(_('Site web'), blank=True)

    facebook = models.URLField(_('Facebook (URL)'), blank=True)
    linkedin = models.URLField(_('LinkedIn (URL)'), blank=True)
    youtube = models.URLField(_('YouTube (URL)'), blank=True)
    x_twitter = models.URLField(_('X / Twitter (URL)'), blank=True)

    ordre_affichage = models.PositiveIntegerField(_('Ordre d\'affichage'), default=0)
    est_actif = models.BooleanField(_('Est actif'), default=True)

    class Meta:
        verbose_name = _('Partenaire')
        verbose_name_plural = _('Partenaires')
        ordering = ['ordre_affichage', 'nom']
        indexes = [
            models.Index(fields=['reference']),
            models.Index(fields=['nom']),
        ]

    def __str__(self):
        return self.nom


class ContactMessage(TimestampedModel):
    MODE_CONTACT_CHOICES = (
        ('whatsapp', _('WhatsApp')),
        ('telephone', _('Téléphone')),
        ('email', _('Email')),
    )

    STATUT_CHOICES = (
        ('nouveau', _('Nouveau')),
        ('lu', _('Lu')),
        ('en_cours', _('En cours')),
        ('repondu', _('Répondu')),
        ('ferme', _('Fermé')),
    )

    nom = models.CharField(_('Nom'), max_length=120)
    postnom = models.CharField(_('Postnom'), max_length=120, blank=True)
    prenom = models.CharField(_('Prénom'), max_length=120, blank=True)

    telephone = models.CharField(_('Téléphone'), max_length=30, validators=[PHONE_REGEX], db_index=True)
    email = models.EmailField(_('Email'), db_index=True)

    sujet = models.CharField(_('Sujet'), max_length=255, blank=True)
    message = models.TextField(_('Message'))

    adresse = models.TextField(_('Adresse'), blank=True)
    ville = models.CharField(_('Ville'), max_length=120, blank=True)
    pays = models.CharField(_('Pays'), max_length=120, blank=True)

    mode_contact_prefere = models.CharField(
        _('Mode de contact préféré'),
        max_length=20,
        choices=MODE_CONTACT_CHOICES,
        default='whatsapp'
    )

    statut = models.CharField(_('Statut'), max_length=20, choices=STATUT_CHOICES, default='nouveau', db_index=True)

    reponse_admin = models.TextField(_('Réponse admin'), blank=True)

    traite_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contact_messages_traitees',
        verbose_name=_('Traité par')
    )
    date_traitement = models.DateTimeField(_('Date de traitement'), null=True, blank=True)

    class Meta:
        verbose_name = _('Message de contact')
        verbose_name_plural = _('Messages de contact')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['telephone']),
            models.Index(fields=['statut']),
        ]

    def __str__(self):
        subject = f" - {self.sujet}" if self.sujet else ""
        name = self.get_full_name()
        return f"{name}{subject} ({self.created_at:%Y-%m-%d})"  # safe even if created_at is set

    def get_full_name(self):
        """
        Retourne le nom complet au format: "nom postnom prenom"
        """
        parts = [self.nom, self.postnom, self.prenom]
        return ' '.join([p for p in parts if p]).strip()
