from django.contrib import admin

# Register your models here.
"""
realisations.admin

Admin configuration for Realisation and Galerie.

Uses only fields present in realisations/models.py and the shared admin
foundation from core (BaseAdmin and admin_mixins). No dynamic checks,
no placeholders, no invented fields.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from core.admin_base import BaseAdmin
from core.admin_mixins import (
    TimestampAdminMixin,
    SlugAdminMixin,
    ImagePreviewMixin,
    SEOAdminMixin,
    PublicationAdminMixin,
    AdminActionsMixin,
)

from .models import Realisation, Galerie


# -----------------------------------------------------------------------------
# Inline: GalerieInline (StackedInline)
# -----------------------------------------------------------------------------
class GalerieInline(ImagePreviewMixin, admin.StackedInline):
    """
    Inline to manage Galerie items directly from a Realisation edit page.

    - StackedInline selected because Galerie contains descriptive fields +
      media files.
    - image_preview is readonly (provided by ImagePreviewMixin) and displayed.
    - show_change_link provides a link to the inline object's change page.
    - ordering by 'ordre' as defined on the model.
    """
    model = Galerie
    extra = 1
    show_change_link = True

    fields = (
        "type_media",
        ("titre_fr", "titre_en"),
        ("description_fr", "description_en"),
        "image",
        "video_url",
        ("ordre", "est_principal"),
        "image_preview",
    )

    readonly_fields = ("image_preview",)
    ordering = ("ordre",)


# -----------------------------------------------------------------------------
# RealisationAdmin
# -----------------------------------------------------------------------------
@admin.register(Realisation)
class RealisationAdmin(
    TimestampAdminMixin,
    SlugAdminMixin,
    ImagePreviewMixin,
    SEOAdminMixin,
    PublicationAdminMixin,
    AdminActionsMixin,
    BaseAdmin,
):
    """
    Administration for Realisation.

    All settings are explicit and use only fields present in realisations/models.py.
    """

    show_full_result_count = True

    # List display: explicit and model-accurate
    list_display = (
        "image_preview",
        "reference",
        "nom_fr",
        "categorie",
        "type_realisation",
        "client",
        "est_confidentiel",
        "badge",
        "est_active",
        "mise_en_avant",
        "ordre_affichage",
        "date_realisation",
    )

    # Filters and search fields based on real model fields
    list_filter = (
        "type_realisation",
        "badge",
        "est_active",
        "mise_en_avant",
        "date_realisation",
        "categorie",
    )

    search_fields = (
        "reference",
        "nom_fr",
        "nom_en",
        "client",
        "secteur_activite",
        "chef_projet",
        "description_fr",
        "description_en",
    )

    ordering = ("-mise_en_avant", "ordre_affichage", "-date_realisation")

    # Optimize FK access to avoid N+1 queries
    list_select_related = ("categorie", "temoignage")

    # Explicit choices for FK form helpers:
    # - autocomplete for 'categorie' (core.CategorieAdmin in this project provides search_fields)
    # - raw_id_fields for 'temoignage' to avoid admin.E039 if contact.Temoignage admin
    #   does not expose search_fields in some deployments.
    autocomplete_fields = ("categorie",)
    raw_id_fields = ("temoignage",)

    # ManyToMany UX
    filter_horizontal = ("services", "produits")

    # Prepopulated slugs from names (fields exist: slug_fr, slug_en)
    prepopulated_fields = {"slug_fr": ("nom_fr",), "slug_en": ("nom_en",)}

    date_hierarchy = "date_realisation"

    # Show image preview in form (TimestampAdminMixin will add created_at/updated_at to readonly_fields)
    readonly_fields = ("image_preview",)

    # Inline galerie editing
    inlines = (GalerieInline,)

    # Explicit, model-accurate fieldsets
    fieldsets = (
        (_("Informations générales"), {
            "fields": (
                "reference",
                ("nom_fr", "nom_en"),
                ("slug_fr", "slug_en"),
                "categorie",
                "type_realisation",
            )
        }),
        (_("Présentation"), {
            "fields": (
                "description_fr",
                "description_en",
                "resume_fr",
                "resume_en",
                "image_principale",
                "image_preview",
                "video_presentation",
            )
        }),
        (_("Informations du projet"), {
            "fields": (
                ("client", "est_confidentiel"),
                "secteur_activite",
            )
        }),
        (_("Localisation"), {
            "fields": (
                ("date_realisation", "ville", "province", "pays"),
                "duree",
            )
        }),
        (_("Équipe"), {
            "fields": ("chef_projet", "equipe_intervention"),
        }),
        (_("Services & Produits"), {
            "fields": ("services", "produits"),
        }),
        (_("Résultats"), {
            "fields": ("resultat_fr", "resultat_en", "temoignage"),
        }),
        (_("Publication"), {
            "fields": ("badge", "est_active", "mise_en_avant", "ordre_affichage"),
        }),
        (_("SEO"), {
            "fields": ("meta_title_fr", "meta_title_en", "meta_description_fr", "meta_description_en"),
            "classes": ("collapse",),
        }),
        (_("Audit"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


# -----------------------------------------------------------------------------
# GalerieAdmin
# -----------------------------------------------------------------------------
@admin.register(Galerie)
class GalerieAdmin(TimestampAdminMixin, ImagePreviewMixin, BaseAdmin):
    """
    Administration for Galerie.
    Uses only fields defined in realisations/models.py.
    """

    show_full_result_count = True

    list_display = ("image_preview", "realisation", "titre_fr", "type_media", "est_principal", "ordre")
    list_filter = ("type_media", "est_principal")
    search_fields = ("titre_fr", "titre_en", "description_fr", "description_en")
    ordering = ("ordre",)

    # Optimize queries when displaying related realisation
    list_select_related = ("realisation",)

    readonly_fields = ("image_preview",)

    fieldsets = (
        (_("Informations"), {
            "fields": ("realisation", "type_media", ("titre_fr", "titre_en"))
        }),
        (_("Description"), {
            "fields": ("description_fr", "description_en")
        }),
        (_("Média"), {
            "fields": ("image", "image_preview", "video_url")
        }),
        (_("Affichage"), {
            "fields": ("ordre", "est_principal")
        }),
        (_("Audit"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
