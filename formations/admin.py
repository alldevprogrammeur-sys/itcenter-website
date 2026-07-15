from django.contrib import admin

# Register your models here.
from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from core.admin_base import BaseAdmin
from core.admin_mixins import (
    TimestampAdminMixin,
    SlugAdminMixin,
    ImagePreviewMixin,
    PDFPreviewMixin,
    SEOAdminMixin,
    PublicationAdminMixin,
    AdminActionsMixin,
)

from .models import Formation, Inscription, FormationMedia


# -----------------------------------------------------------------------------
# Inline for FormationMedia
# Use StackedInline because media records include multiple fields (files + text)
# -----------------------------------------------------------------------------
class FormationMediaInline(ImagePreviewMixin, PDFPreviewMixin, admin.StackedInline):
    model = FormationMedia
    extra = 1
    fields = (
        "type_media",
        "titre_fr",
        "titre_en",
        "description_fr",
        "description_en",
        "image",
        "document",
        "video_url",
        "ordre_affichage",
        "est_active",
    )
    readonly_fields = ("image_preview", "pdf_preview")
    show_change_link = True
    ordering = ("ordre_affichage",)


# -----------------------------------------------------------------------------
# FormationAdmin
# -----------------------------------------------------------------------------
@admin.register(Formation)
class FormationAdmin(
    TimestampAdminMixin,
    SlugAdminMixin,
    ImagePreviewMixin,
    PDFPreviewMixin,
    SEOAdminMixin,
    PublicationAdminMixin,
    AdminActionsMixin,
    BaseAdmin,
):
    """
    Admin for Formation model.

    Uses only fields actually defined in formations.models.Formation.
    """

    show_full_result_count = True

    list_display = (
        "image_preview",
        "reference",
        "nom_fr",
        "type_formation",
        "categorie",
        "formateur",
        "est_active",
        "mise_en_avant",
        "ordre_affichage",
        "date_publication",
    )

    list_filter = ("type_formation", "est_active", "mise_en_avant", "categorie", "formateur")
    search_fields = ("reference", "nom_fr", "nom_en", "description_fr", "description_en")
    ordering = ("-mise_en_avant", "ordre_affichage", "nom_fr")

    # Use select_related for FK columns shown in list_display for performance
    list_select_related = ("categorie", "formateur")

    # Autocomplete and many-to-many handling
    autocomplete_fields = ("categorie", "formateur")
    filter_horizontal = ("competences",)

    # Prepopulate slugs from names (fields exist: slug_fr, slug_en)
    prepopulated_fields = {"slug_fr": ("nom_fr",), "slug_en": ("nom_en",)}

    inlines = (FormationMediaInline,)

    # Date hierarchy on date_publication (field exists on model)
    date_hierarchy = "date_publication"

    # Readonly previews; timestamps handled by TimestampAdminMixin
    readonly_fields = ("image_preview", "pdf_preview")

    fieldsets = (
        (_("Informations générales"), {
            "fields": (
                "reference",
                ("nom_fr", "nom_en"),
                ("slug_fr", "slug_en"),
                "categorie",
                "type_formation",
            )
        }),
        (_("Présentation"), {
            "fields": (
                "description_fr",
                "description_en",
                "image_principale",
                "brochure_pdf",
                "video_presentation",
            )
        }),
        (_("Informations pédagogiques"), {
            "fields": (
                ("niveau", "duree_valeur", "duree_unite", "duree_heures"),
                ("prix", "devise", "places_max"),
            )
        }),
        (_("Formateur & Compétences"), {
            "fields": ("formateur", "competences")
        }),
        (_("Contenu pédagogique"), {
            "fields": (
                ("prerequis_fr", "prerequis_en"),
                ("objectif_fr", "objectif_en"),
                ("debouches_fr", "debouches_en"),
                ("public_cible_fr", "public_cible_en"),
                ("materiel_fourni_fr", "materiel_fourni_en"),
            )
        }),
        (_("Certificat"), {"fields": ("certificat", "type_certificat")}),
        (_("SEO"), {
            "fields": ("meta_title_fr", "meta_title_en", "meta_description_fr", "meta_description_en"),
            "classes": ("collapse",),
        }),
        (_("Publication"), {
            "fields": ("est_active", "mise_en_avant", "ordre_affichage", "date_publication", "galerie_active")
        }),
        (_("Audit"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


# -----------------------------------------------------------------------------
# InscriptionAdmin
# -----------------------------------------------------------------------------
@admin.register(Inscription)
class InscriptionAdmin(TimestampAdminMixin, PDFPreviewMixin, BaseAdmin):
    """
    Admin for Inscription.
    """

    show_full_result_count = True

    list_display = (
        "formation",
        "nom",
        "prenom",
        "email",
        "telephone",
        "statut",
        "created_at",
    )

    list_filter = ("statut", "mode_formation", "type_demande")
    search_fields = ("nom", "prenom", "email", "telephone")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    # Optimize queries
    list_select_related = ("formation",)

    # readonly previews and PDF flag; timestamps via mixin
    readonly_fields = ("pdf_preview", "pdf_genere")

    autocomplete_fields = ("formation",)

    fieldsets = (
        (_("Informations personnelles"), {
            "fields": (("nom", "postnom", "prenom"), ("sexe", "date_naissance"))
        }),
        (_("Coordonnées"), {"fields": ("email", "telephone")}),
        (_("Adresse"), {"fields": ("pays", "province", "ville", "adresse_complete")}),
        (_("Formation & Type"), {"fields": ("formation", "mode_formation", "type_demande")}),
        (_("Compléments"), {"fields": ("nom_entreprise", "nom_groupe", "nombre_participants", "message")}),
        (_("Statut & PDF"), {"fields": ("statut", "pdf_preview", "pdf_genere")}),
        (_("Audit"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    # Simplified actions: update queryset directly (statut field exists)
    @admin.action(description=_("Valider la sélection"))
    def action_valider(self, request, queryset):
        updated = queryset.update(statut="confirme")
        messages.success(request, _("%d inscription(s) validée(s).") % updated)

    @admin.action(description=_("Refuser la sélection"))
    def action_refuser(self, request, queryset):
        updated = queryset.update(statut="annule")
        messages.success(request, _("%d inscription(s) refusée(s).") % updated)

    @admin.action(description=_("Archiver la sélection (mise en attente)"))
    def action_archiver(self, request, queryset):
        updated = queryset.update(statut="en_attente")
        messages.success(request, _("%d inscription(s) archivée(s).") % updated)

    actions = ("action_valider", "action_refuser", "action_archiver")


# -----------------------------------------------------------------------------
# FormationMediaAdmin
# -----------------------------------------------------------------------------
@admin.register(FormationMedia)
class FormationMediaAdmin(
    TimestampAdminMixin,
    ImagePreviewMixin,
    PDFPreviewMixin,
    AdminActionsMixin,
    BaseAdmin,
):
    """
    Admin for FormationMedia.
    """

    show_full_result_count = True

    list_display = ("image_preview", "titre_fr", "type_media", "ordre_affichage", "est_active")
    list_filter = ("type_media", "est_active")
    search_fields = ("titre_fr", "titre_en", "description_fr", "description_en")
    ordering = ("ordre_affichage",)

    # Optimize queries when showing formation in lists
    list_select_related = ("formation",)

    readonly_fields = ("image_preview", "pdf_preview")

    fieldsets = (
        (None, {"fields": ("formation", "type_media", ("titre_fr", "titre_en"))}),
        (_("Description"), {"fields": ("description_fr", "description_en")}),
        (_("Fichiers"), {"fields": ("image", "document", "video_url")}),
        (_("Affichage"), {"fields": ("ordre_affichage", "est_active")}),
        (_("Audit"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )