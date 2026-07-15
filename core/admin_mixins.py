"""
core.admin_mixins
-----------------

Mixins réutilisables pour les ModelAdmin du projet IT CENTER.

Fournit :
- FieldCheckMixin : utilitaire pour tester l'existence d'un champ.
- TimestampAdminMixin
- ReferenceAdminMixin
- SlugAdminMixin
- PublicationAdminMixin
- SEOAdminMixin
- DisplayMixin (contient image_preview et pdf_preview)
- ImagePreviewMixin / PDFPreviewMixin (alias pour compatibilité)
- AdminActionsMixin (actions modernes, robustes et non-invasives)

Les mixins vérifient l'existence des champs avant toute opération, ce qui
permet leur réutilisation sur des modèles hétérogènes.
"""

from typing import Tuple

from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Model
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


class FieldCheckMixin:
    """
    Utilitaire pour vérifier la présence d'un champ sur le modèle lié à
    l'instance ModelAdmin.

    Les méthodes doivent rester sûres et ne jamais propager d'exception.
    """

    def _has_field(self, field_name: str) -> bool:
        """
        Retourne True si le modèle exposé par ce ModelAdmin possède
        le champ `field_name`.
        """
        model = getattr(self, "model", None)
        if model is None:
            return False
        try:
            model._meta.get_field(field_name)
            return True
        except FieldDoesNotExist:
            return False
        except Exception:
            return False


# ---------------------------------------------------------------------
# A. TimestampAdminMixin
# ---------------------------------------------------------------------
class TimestampAdminMixin(FieldCheckMixin):
    """
    Ajoute created_at / updated_at aux readonly_fields si le modèle les a.
    """

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj) or [])
        for ts in ("created_at", "updated_at"):
            if self._has_field(ts) and ts not in readonly:
                readonly.append(ts)
        return tuple(readonly)


# ---------------------------------------------------------------------
# B. ReferenceAdminMixin
# ---------------------------------------------------------------------
class ReferenceAdminMixin(FieldCheckMixin):
    """
    Prépare la gestion du champ `reference` :
    - le rend readonly s'il existe
    - l'ajoute aux search_fields s'il existe

    Important : ce mixin ne modifie plus automatiquement list_display.
    """

    reference_field_name = "reference"

    def get_search_fields(self, request) -> Tuple[str, ...]:
        search_fields = list(super().get_search_fields(request) or [])
        if self._has_field(self.reference_field_name) and self.reference_field_name not in search_fields:
            search_fields.insert(0, self.reference_field_name)
        return tuple(search_fields)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj) or [])
        if self._has_field(self.reference_field_name) and self.reference_field_name not in readonly:
            readonly.append(self.reference_field_name)
        return tuple(readonly)


# ---------------------------------------------------------------------
# C. SlugAdminMixin
# ---------------------------------------------------------------------
class SlugAdminMixin(FieldCheckMixin):
    """
    Configure dynamiquement prepopulated_fields pour les paires :
      nom_fr -> slug_fr
      nom_en -> slug_en

    Le mixin est facilement surchargeable (changer slug_map si besoin).
    """

    slug_map = (("nom_fr", "slug_fr"), ("nom_en", "slug_en"))

    def get_prepopulated_fields(self, request, obj=None):
        prepop = dict(getattr(self, "prepopulated_fields", {}) or {})
        for source, target in self.slug_map:
            if self._has_field(source) and self._has_field(target):
                prepop[target] = (source,)
        return prepop


# ---------------------------------------------------------------------
# D. PublicationAdminMixin
# ---------------------------------------------------------------------
class PublicationAdminMixin(FieldCheckMixin):
    """
    Fournit list_filter et ordering basés sur les champs de publication :
    - est_active
    - mise_en_avant
    - ordre_affichage

    Le mixin n'essaie pas de gérer list_editable (contrainte Django), il
    ajoute uniquement list_filter et ordering si les champs existent.
    """

    def get_list_filter(self, request):
        base = list(super().get_list_filter(request) or [])
        for fld in ("est_active", "mise_en_avant"):
            if self._has_field(fld) and fld not in base:
                base.append(fld)
        return tuple(base)

    def get_ordering(self, request):
        ordering = list(super().get_ordering(request) or [])
        default = []
        if self._has_field("mise_en_avant"):
            default.append("-mise_en_avant")
        if self._has_field("ordre_affichage"):
            default.append("ordre_affichage")
        for d in default:
            if d not in ordering:
                ordering.insert(0, d)
        return tuple(ordering)


# ---------------------------------------------------------------------
# E. SEOAdminMixin
# ---------------------------------------------------------------------
class SEOAdminMixin:
    """
    Fournit un fieldset SEO réutilisable.

    Usage :
        class MyAdmin(SEOAdminMixin, admin.ModelAdmin):
            fieldsets = (
                (None, {'fields': (...) }),
                *SEOAdminMixin.get_seo_fieldset(),
            )
    """

    seo_fields = (
        "meta_title_fr",
        "meta_title_en",
        "meta_description_fr",
        "meta_description_en",
    )

    @classmethod
    def get_seo_fieldset(cls):
        return (_("SEO"), {"fields": tuple(cls.seo_fields)}),


# ---------------------------------------------------------------------
# I. DisplayMixin (regroupe méthodes @admin.display)
# ---------------------------------------------------------------------
class DisplayMixin(FieldCheckMixin):
    """
    Centralise les méthodes d'affichage destinées à l'interface d'administration.

    Contient image_preview et pdf_preview. Peut être étendu avec d'autres
    méthodes décorées par @admin.display (badge_display, status_display, ...).
    """

    # Configuration par défaut ; classes enfants peuvent surcharger.
    image_field_names = ("image_principale", "photo", "image")
    image_preview_width = 120
    pdf_field_name = "brochure_pdf"
    empty_value_display = "—"

    @admin.display(description=_("Aperçu"))
    def image_preview(self, obj: Model):
        """
        Retourne une balise <img> sécurisée ou empty_value_display si aucune
        image n'est disponible.
        """
        for field_name in self.image_field_names:
            if not self._has_field(field_name):
                continue
            try:
                value = getattr(obj, field_name)
            except Exception:
                continue
            if not value:
                continue
            url = getattr(value, "url", None)
            if not url:
                continue
            return format_html(
                '<img src="{}" width="{}" style="object-fit:contain; max-height:120px;" alt="{}" />',
                url,
                self.image_preview_width,
                _("Aperçu image"),
            )
        return self.empty_value_display

    @admin.display(description=_("PDF"))
    def pdf_preview(self, obj: Model):
        """
        Retourne un lien 'Voir le PDF' si le champ pdf_field_name contient un
        fichier, sinon empty_value_display.
        """
        if not self._has_field(self.pdf_field_name):
            return self.empty_value_display
        try:
            file_field = getattr(obj, self.pdf_field_name)
        except Exception:
            return self.empty_value_display
        if not file_field:
            return self.empty_value_display
        url = getattr(file_field, "url", None)
        if not url:
            return self.empty_value_display
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">{}</a>',
            url,
            _("Voir le PDF"),
        )


# Backwards-compatible aliases
class ImagePreviewMixin(DisplayMixin):
    """
    Alias pour compatibilité : expose image_preview via DisplayMixin.
    """
    pass


class PDFPreviewMixin(DisplayMixin):
    """
    Alias pour compatibilité : expose pdf_preview via DisplayMixin.
    """
    pass


# ---------------------------------------------------------------------
# H. AdminActionsMixin
# ---------------------------------------------------------------------
class AdminActionsMixin(FieldCheckMixin):
    """
    Actions génériques réutilisables :
    - activer (est_active = True)
    - desactiver (est_active = False)
    - mettre_en_avant (mise_en_avant = True)
    - retirer_de_la_une (mise_en_avant = False)

    Les actions vérifient l'existence des champs avant mise à jour et n'érigent
    pas d'erreur si le champ est absent.
    """

    @admin.action(description=_("Activer la sélection"))
    def action_activer(self, request, queryset):
        if not self._has_field("est_active"):
            messages.warning(request, _("Le modèle ne possède pas le champ 'est_active'."))
            return
        updated = queryset.update(est_active=True)
        messages.success(request, _("%d enregistrement(s) activé(s).") % updated)

    @admin.action(description=_("Désactiver la sélection"))
    def action_desactiver(self, request, queryset):
        if not self._has_field("est_active"):
            messages.warning(request, _("Le modèle ne possède pas le champ 'est_active'."))
            return
        updated = queryset.update(est_active=False)
        messages.success(request, _("%d enregistrement(s) désactivé(s).") % updated)

    @admin.action(description=_("Mettre en avant"))
    def action_mettre_en_avant(self, request, queryset):
        if not self._has_field("mise_en_avant"):
            messages.warning(request, _("Le modèle ne possède pas le champ 'mise_en_avant'."))
            return
        updated = queryset.update(mise_en_avant=True)
        messages.success(request, _("%d enregistrement(s) mis en avant.") % updated)

    @admin.action(description=_("Retirer de la une"))
    def action_retirer_de_la_une(self, request, queryset):
        if not self._has_field("mise_en_avant"):
            messages.warning(request, _("Le modèle ne possède pas le champ 'mise_en_avant'."))
            return
        updated = queryset.update(mise_en_avant=False)
        messages.success(request, _("%d enregistrement(s) retiré(s) de la une.") % updated)