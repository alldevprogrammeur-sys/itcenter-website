from django.contrib import admin

# Register your models here.
"""
core.admin

Admin registrations for core models (ParametreSite, Categorie, Poste).

This module is strictly aligned with core/models.py: it uses only real fields
defined there and reuses the admin foundation (BaseAdmin and mixins) without
modifying them.

No placeholders, no assumptions, no invented fields.
"""

from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from . import models as core_models
from .admin_base import BaseAdmin
from .admin_mixins import (
    TimestampAdminMixin,
    SlugAdminMixin,
    ImagePreviewMixin,
    PDFPreviewMixin,
    AdminActionsMixin,
)

from django.contrib import admin
from .models import Membre


def _model_has_field(model, field_name: str) -> bool:
    """
    Safe check if `model` has a field named `field_name`.
    """
    try:
        model._meta.get_field(field_name)
        return True
    except Exception:
        return False


# -----------------------------------------------------------------------------
# ParametreSiteAdmin (singleton)
# -----------------------------------------------------------------------------
@admin.register(core_models.ParametreSite)
class ParametreSiteAdmin(
    TimestampAdminMixin,
    ImagePreviewMixin,
    PDFPreviewMixin,
    BaseAdmin,
):
    """
    Admin for ParametreSite (singleton).

    Fieldsets are explicit and use only fields defined on core.models.ParametreSite.
    The admin enforces the singleton constraint: no second instance can be added,
    deletion via admin is disabled, and changelist redirects to the edit page when
    an instance exists.
    """

    # Explicit list_display using existing fields
    list_display = ("site_name", "langue_par_defaut", "site_actif")
    list_filter = ("site_actif", "langue_par_defaut")
    search_fields = ("site_name", "adresse", "email_principal", "email_secondaire")

    # Configure ImagePreviewMixin to look at 'logo' (real field)
    image_field_names = ("logo", "favicon")
    # PDFPreviewMixin default pdf_field_name = "brochure_pdf" — ParametreSite doesn't
    # define it, pdf_preview will return empty value display.

    readonly_fields = ("image_preview", "pdf_preview")  # Timestamp mixin will add created_at/updated_at

    def has_add_permission(self, request):
        """
        Prevent adding a second instance (singleton).
        """
        if core_models.ParametreSite.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        """
        Disallow deletion via admin for safety.
        """
        return False

    def save_model(self, request, obj, form, change):
        """
        Extra guard against creating a second instance.
        """
        if not change and core_models.ParametreSite.objects.exists():
            messages.error(
                request,
                _("Une configuration existe déjà. La création d'une seconde instance est interdite."),
            )
            return
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        """
        If an instance exists, redirect to its change page (singleton UX).
        """
        qs = self.get_queryset(request)
        obj = qs.first()
        if obj:
            change_url = reverse(
                f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
                args=(obj.pk,),
            )
            return redirect(change_url)
        return super().changelist_view(request, extra_context=extra_context)

    def get_fieldsets(self, request, obj=None):
        """
        Build explicit fieldsets using only the real fields defined on the model.
        """
        model = core_models.ParametreSite
        fieldsets = []

        # Informations générales
        general = []
        for f in ("site_name", "logo", "favicon", "adresse", "langue_par_defaut", "site_actif"):
            if _model_has_field(model, f):
                general.append(f)
        if general:
            fieldsets.append((_("Informations générales"), {"fields": tuple(general)}))

        # Coordonnées
        coord = []
        for f in ("telephone_1", "telephone_2", "telephone_3", "email_principal", "email_secondaire"):
            if _model_has_field(model, f):
                coord.append(f)
        if coord:
            fieldsets.append((_("Coordonnées"), {"fields": tuple(coord)}))

        # Couleurs / Google Maps
        config = []
        for f in ("couleur_primaire", "couleur_secondaire", "google_maps_embed"):
            if _model_has_field(model, f):
                config.append(f)
        if config:
            fieldsets.append((_("Configuration"), {"fields": tuple(config)}))

        # Réseaux sociaux
        socials = []
        for f in (
            "facebook_url",
            "linkedin_url",
            "youtube_url",
            "instagram_url",
            "telegram_url",
            "whatsapp",
            "x_url",
            "tiktok_url",
            "github_url",
        ):
            if _model_has_field(model, f):
                socials.append(f)
        if socials:
            fieldsets.append((_("Réseaux sociaux"), {"fields": tuple(socials)}))

        # Aperçus (logo)
        previews = []
        if _model_has_field(model, "logo") or _model_has_field(model, "favicon"):
            previews.append("image_preview")
        # ParametreSite has no brochure_pdf field in the model; pdf_preview will be safe.
        if previews:
            fieldsets.append((_("Aperçus"), {"fields": tuple(previews)}))

        # SEO (ParametreSite uses seo_meta_title / seo_meta_description)
        seo = []
        if _model_has_field(model, "seo_meta_title"):
            seo.append("seo_meta_title")
        if _model_has_field(model, "seo_meta_description"):
            seo.append("seo_meta_description")
        if seo:
            fieldsets.append((_("SEO"), {"fields": tuple(seo), "classes": ("collapse",)}))

        # Audit
        audit = []
        for f in ("created_at", "updated_at"):
            if _model_has_field(model, f):
                audit.append(f)
        if audit:
            fieldsets.append((_("Audit"), {"fields": tuple(audit), "classes": ("collapse",)}))

        return tuple(fieldsets)


# -----------------------------------------------------------------------------
# CategorieAdmin
# -----------------------------------------------------------------------------
@admin.register(core_models.Categorie)
class CategorieAdmin(
    TimestampAdminMixin,
    SlugAdminMixin,
    ImagePreviewMixin,
    AdminActionsMixin,
    BaseAdmin,
):
    """
    Admin for Categorie.

    Uses fields exactly from core.models.Categorie:
      - nom_fr, nom_en, slug, description_fr, description_en, image, actif
    """

    # Explicit list_display based on real fields
    list_display = ("image_preview", "nom_fr", "nom_en", "slug", "actif")
    list_filter = ("actif",)
    search_fields = ("nom_fr", "nom_en", "slug")
    ordering = ("nom_fr",)
    prepopulated_fields = {"slug": ("nom_fr",)}

    # Fieldsets explicit and readable
    fieldsets = (
        (None, {"fields": ("nom_fr", "nom_en", "slug")}),
        (_("Contenu"), {"fields": ("description_fr", "description_en", "image")}),
        (_("Affichage"), {"fields": ("actif",)}),
        (_("Audit"), {"fields": tuple(f for f in ("created_at", "updated_at") if _model_has_field(core_models.Categorie, f)), "classes": ("collapse",)}),
    )


# -----------------------------------------------------------------------------
# PosteAdmin
# -----------------------------------------------------------------------------
@admin.register(core_models.Poste)
class PosteAdmin(
    TimestampAdminMixin,
    SlugAdminMixin,
    AdminActionsMixin,
    BaseAdmin,
):
    """
    Admin for Poste.

    Uses fields exactly from core.models.Poste:
      - nom_fr, nom_en, slug, description, image
    """

    list_display = ("nom_fr", "nom_en", "slug")
    search_fields = ("nom_fr", "nom_en", "slug")
    ordering = ("nom_fr",)
    prepopulated_fields = {"slug": ("nom_fr",)}

    fieldsets = (
        (None, {"fields": ("nom_fr", "nom_en", "slug")}),
        (_("Description"), {"fields": ("description", "image")}),
        (_("Audit"), {"fields": tuple(f for f in ("created_at", "updated_at") if _model_has_field(core_models.Poste, f)), "classes": ("collapse",)}),
    )


@admin.register(Membre)
class MembreAdmin(admin.ModelAdmin):
    # Remplace 'nom' et 'prenom' par les vrais noms de champs de ton modèle Membre
    search_fields = ['nom', 'prenom']
