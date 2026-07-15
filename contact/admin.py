from django.contrib import admin

# Register your models here.
"""
contact.admin

Administration pour les modèles de l'application `contact`.

Ce fichier est strictement aligné sur contact/models.py fourni :
- n'invente aucun champ,
- n'utilise que les champs réels,
- réutilise la fondation d'admin (core.admin_base.BaseAdmin et core.admin_mixins)
  sans les modifier.

Modèles enregistrés :
- Membre
- Temoignage
- Partenaire
- ContactMessage

Le module inclut une logique sûre et explicite pour choisir entre
autocomplete_fields et raw_id_fields afin d'éviter l'erreur admin.E039 :
si le ModelAdmin cible expose search_fields, on active autocomplete ; sinon
on bascule sur raw_id_fields.
"""

from django import apps as dj_apps
from django.contrib import admin
from django.conf import settings
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from core.admin_base import BaseAdmin
from core.admin_mixins import (
    TimestampAdminMixin,
    ImagePreviewMixin,
    PublicationAdminMixin,
    AdminActionsMixin,
)

from .models import Membre, Temoignage, Partenaire, ContactMessage


# ---------------------------------------------------------------------------
# Helper: détecte si l'admin du modèle lié expose search_fields
# ---------------------------------------------------------------------------
def _modeladmin_has_search_fields(model_cls) -> bool:
    """
    Retourne True si un ModelAdmin est enregistré pour model_cls
    et qu'il expose search_fields non vide.

    Utilisé pour décider entre autocomplete_fields et raw_id_fields.
    """
    try:
        ma = admin.site._registry.get(model_cls)
        if ma is None:
            return False
        sf = getattr(ma, "search_fields", None)
        return bool(sf)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# MembreAdmin
# ---------------------------------------------------------------------------
@admin.register(Membre)
class MembreAdmin(
    TimestampAdminMixin,
    ImagePreviewMixin,
    PublicationAdminMixin,
    AdminActionsMixin,
    BaseAdmin,
):
    """
    Administration pour Membre. Utilise uniquement les champs définis dans
    contact/models.py. ImagePreviewMixin est configuré pour utiliser le champ
    'photo' du modèle Membre.
    """

    # Ergonomie
    list_per_page = 25
    save_on_top = True
    show_full_result_count = True

    image_field_names = ("photo",)

    # Liste
    list_display = (
        "image_preview",
        "reference",
        "get_full_name",
        "poste",
        "ordre_affichage",
        "date_entree",
        "est_fondateur",
        "est_actif",
        "mise_en_avant",
    )
    list_display_links = ("reference", "get_full_name")
    list_filter = ("est_actif", "mise_en_avant", "est_fondateur")
    search_fields = ("reference", "nom", "postnom", "prenom", "email")
    ordering = ("-mise_en_avant", "ordre_affichage", "nom")

    # Performance : FK -> poste
    list_select_related = ("poste",)

    # Choix between autocomplete or raw_id for poste to avoid admin.E039
    _poste_model = getattr(Membre, "poste").field.related_model
    if _modeladmin_has_search_fields(_poste_model):
        autocomplete_fields = ("poste",)
        raw_id_fields = ()
    else:
        autocomplete_fields = ()
        raw_id_fields = ("poste",)

    # Readonly previews (timestamps handled by TimestampAdminMixin)
    readonly_fields = ("image_preview",)

    # Fieldsets explicites (utilisent uniquement des champs réels)
    fieldsets = (
        (_("Identité"), {"fields": ("reference", ("nom", "postnom", "prenom"), "photo", "image_preview")}),
        (_("Fonction"), {"fields": ("poste", ("fonction_fr", "fonction_en"))}),
        (_("Biographie"), {"fields": ("biographie_fr", "biographie_en")}),
        (_("Coordonnées"), {"fields": ("telephone", "email")}),
        (_("Réseaux sociaux"), {"fields": ("facebook", "linkedin", "github", "x_twitter", "instagram")}),
        (_("Affichage & statut"), {"fields": ("ordre_affichage", "date_entree", "est_fondateur", "est_actif", "mise_en_avant")}),
        (_("Audit"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


# ---------------------------------------------------------------------------
# TemoignageAdmin
# ---------------------------------------------------------------------------
@admin.register(Temoignage)
class TemoignageAdmin(TimestampAdminMixin, ImagePreviewMixin, BaseAdmin):
    """
    Administration pour Temoignage.

    Les relations optionnelles (formation, service, produit, realisation)
    utilisent autocomplete_fields si le ModelAdmin cible définit search_fields,
    sinon raw_id_fields pour garantir la compatibilité admin.E039.
    """

    list_per_page = 25
    save_on_top = True
    show_full_result_count = True

    image_field_names = ("photo",)

    list_display = ("image_preview", "get_full_name", "entreprise", "note", "origine", "est_valide", "mise_en_avant")
    list_display_links = ("get_full_name",)
    list_filter = ("origine", "note", "est_valide", "mise_en_avant")
    search_fields = ("nom", "postnom", "prenom", "entreprise", "message_fr", "message_en")
    ordering = ("-mise_en_avant", "-created_at")

    # Relations optionnelles définies dans le modèle
    related_map = {
        "formation": getattr(Temoignage, "formation").field.related_model,
        "service": getattr(Temoignage, "service").field.related_model,
        "produit": getattr(Temoignage, "produit").field.related_model,
        "realisation": getattr(Temoignage, "realisation").field.related_model,
    }

    autocomplete_fields_list = []
    raw_id_fields_list = []
    for name, model_cls in related_map.items():
        if model_cls is None:
            raw_id_fields_list.append(name)
        elif _modeladmin_has_search_fields(model_cls):
            autocomplete_fields_list.append(name)
        else:
            raw_id_fields_list.append(name)

    autocomplete_fields = tuple(autocomplete_fields_list)
    raw_id_fields = tuple(raw_id_fields_list)

    # Optimize queries if useful
    list_select_related = tuple(name for name in related_map.keys())

    readonly_fields = ("image_preview",)

    fieldsets = (
        (_("Identité"), {"fields": (("nom", "postnom", "prenom"), "photo", "image_preview")}),
        (_("Fonction & entreprise"), {"fields": ("fonction_fr", "fonction_en", "entreprise")}),
        (_("Message"), {"fields": ("message_fr", "message_en", "note")}),
        (_("Origine / Liens"), {"fields": tuple(f for f in ("origine", "formation", "service", "produit", "realisation") if hasattr(Temoignage, f))}),
        (_("Publication"), {"fields": ("est_valide", "mise_en_avant")}),
        (_("Audit"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


# ---------------------------------------------------------------------------
# PartenaireAdmin
# ---------------------------------------------------------------------------
@admin.register(Partenaire)
class PartenaireAdmin(TimestampAdminMixin, ImagePreviewMixin, PublicationAdminMixin, BaseAdmin):
    """
    Administration pour Partenaire. ImagePreviewMixin utilise le champ 'logo'.
    """

    list_per_page = 25
    save_on_top = True
    show_full_result_count = True

    image_field_names = ("logo",)

    list_display = ("image_preview", "reference", "nom", "type", "ordre_affichage", "est_actif")
    list_display_links = ("reference", "nom")
    list_filter = ("type", "est_actif")
    search_fields = ("reference", "nom", "site_web")
    ordering = ("ordre_affichage", "nom")

    readonly_fields = ("image_preview",)

    fieldsets = (
        (_("Informations générales"), {"fields": ("reference", "nom", "logo", "image_preview")}),
        (_("Présentation"), {"fields": ("description_fr", "description_en")}),
        (_("Détails"), {"fields": ("type", "site_web")}),
        (_("Réseaux sociaux"), {"fields": ("facebook", "linkedin", "youtube", "x_twitter")}),
        (_("Affichage"), {"fields": ("ordre_affichage", "est_actif")}),
        (_("Audit"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


# ---------------------------------------------------------------------------
# ContactMessageAdmin
# ---------------------------------------------------------------------------
@admin.register(ContactMessage)
class ContactMessageAdmin(TimestampAdminMixin, BaseAdmin):
    """
    Administration pour ContactMessage.

    Pour traite_par (FK vers AUTH_USER_MODEL), on bascule entre
    autocomplete_fields et raw_id_fields selon la présence de search_fields
    sur l'admin de la target model afin d'éviter admin.E039.
    """

    list_per_page = 25
    save_on_top = True
    show_full_result_count = True

    list_display = ("get_full_name", "email", "telephone", "mode_contact_prefere", "statut", "traite_par", "created_at")
    list_display_links = ("get_full_name",)
    list_filter = ("mode_contact_prefere", "statut")
    search_fields = ("nom", "postnom", "prenom", "email", "telephone")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    list_select_related = ("traite_par",)

    # Resolve user model class robustly and decide autocomplete vs raw_id
    try:
        user_model = dj_apps.get_model(settings.AUTH_USER_MODEL)
    except Exception:
        user_model = None

    if user_model and _modeladmin_has_search_fields(user_model):
        autocomplete_fields = ("traite_par",)
        raw_id_fields = ()
    else:
        autocomplete_fields = ()
        raw_id_fields = ("traite_par",)

    readonly_fields = ("date_traitement",)

    fieldsets = (
        (_("Identité"), {"fields": (("nom", "postnom", "prenom"),)}),
        (_("Coordonnées"), {"fields": ("telephone", "email")}),
        (_("Message"), {"fields": ("sujet", "message")}),
        (_("Adresse"), {"fields": ("adresse", "ville", "pays")}),
        (_("Préférences"), {"fields": ("mode_contact_prefere",)}),
        (_("Traitement"), {"fields": ("statut", "reponse_admin", "traite_par", "date_traitement")}),
        (_("Audit"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    # Actions admin : correspondent exactement aux STATUT_CHOICES du modèle
    @admin.action(description=_("Marquer comme 'Nouveau'"))
    def mark_nouveau(self, request, queryset):
        updated = queryset.update(statut="nouveau")
        messages.success(request, _("%d message(s) marqué(s) comme 'Nouveau'.") % updated)

    @admin.action(description=_("Marquer comme 'Lu'"))
    def mark_lu(self, request, queryset):
        updated = queryset.update(statut="lu")
        messages.success(request, _("%d message(s) marqué(s) comme 'Lu'.") % updated)

    @admin.action(description=_("Marquer comme 'En cours'"))
    def mark_en_cours(self, request, queryset):
        updated = queryset.update(statut="en_cours")
        messages.success(request, _("%d message(s) marqué(s) comme 'En cours'.") % updated)

    @admin.action(description=_("Marquer comme 'Répondu'"))
    def mark_repondu(self, request, queryset):
        updated = queryset.update(statut="repondu")
        messages.success(request, _("%d message(s) marqué(s) comme 'Répondu'.") % updated)

    @admin.action(description=_("Marquer comme 'Fermé'"))
    def mark_ferme(self, request, queryset):
        updated = queryset.update(statut="ferme")
        messages.success(request, _("%d message(s) marqué(s) comme 'Fermé'.") % updated)

    actions = ("mark_nouveau", "mark_lu", "mark_en_cours", "mark_repondu", "mark_ferme")