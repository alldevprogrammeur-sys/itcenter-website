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

from .models import Service, DemandeService


# -----------------------------------------------------------------------------
# ServiceAdmin
# -----------------------------------------------------------------------------
@admin.register(Service)
class ServiceAdmin(
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
    Admin for Service model. Uses only real fields defined in services.models.Service.
    """

    show_full_result_count = True

    # Explicit list_display including categorie as requested
    list_display = (
        "image_preview",
        "reference",
        "nom_fr",
        "nom_en",
        "categorie",
        "badge",
        "est_active",
        "mise_en_avant",
        "ordre_affichage",
        "date_publication",
    )

    list_filter = ("badge", "est_active", "mise_en_avant", "categorie", "date_publication")
    search_fields = ("reference", "nom_fr", "nom_en", "description_fr", "description_en", "inclus_fr", "inclus_en")
    ordering = ("-mise_en_avant", "ordre_affichage", "nom_fr")

    # Optimize queries: service list shows categorie
    list_select_related = ("categorie",)

    # Autocomplete for category (core.Categorie admin must provide search_fields)
    autocomplete_fields = ("categorie",)

    prepopulated_fields = {"slug_fr": ("nom_fr",), "slug_en": ("nom_en",)}

    readonly_fields = ("image_preview", "pdf_preview")

    fieldsets = (
        (_("Informations générales"), {
            "fields": (
                "reference",
                ("nom_fr", "nom_en"),
                ("slug_fr", "slug_en"),
                "categorie",
                "badge",
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
        (_("Détails commerciaux"), {
            "fields": (
                ("prix_sur_devis",),
                ("inclus_fr", "inclus_en"),
                ("public_cible_fr", "public_cible_en"),
            )
        }),
        (_("Apparence & SEO"), {
            "fields": ("icone", "couleur", "meta_title_fr", "meta_title_en", "meta_description_fr", "meta_description_en"),
            "classes": ("collapse",),
        }),
        (_("Publication"), {
            "fields": ("est_active", "mise_en_avant", "ordre_affichage", "date_publication")
        }),
        (_("Audit"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


# -----------------------------------------------------------------------------
# DemandeServiceAdmin
# -----------------------------------------------------------------------------
@admin.register(DemandeService)
class DemandeServiceAdmin(TimestampAdminMixin, PDFPreviewMixin, BaseAdmin):
    """
    Admin for DemandeService.
    Uses only real fields present in services.models.DemandeService.
    """

    show_full_result_count = True

    list_display = (
        "service",
        "nom",
        "prenom",
        "email",
        "telephone",
        "type_client",
        "statut",
        "created_at",
    )

    list_filter = ("statut", "type_client", "niveau_urgence", "mode_contact_prefere", "source_demande")
    search_fields = ("nom", "postnom", "prenom", "email", "telephone", "nom_organisation")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    # Optimize queries: follow FK to service and traite_par
    list_select_related = ("service", "traite_par")

    # Use autocomplete for service (ServiceAdmin defines search_fields)
    autocomplete_fields = ("service",)
    # Use raw_id_fields for traite_par to avoid dependence on User admin search_fields
    raw_id_fields = ("traite_par",)

    # Ensure pdf_preview uses the correct field present on the model
    pdf_field_name = "pdf_file"
    readonly_fields = ("pdf_preview", "pdf_genere", "date_traitement")

    fieldsets = (
        (_("Informations personnelles"), {
            "fields": (("nom", "postnom", "prenom"), ("telephone", "email"))
        }),
        (_("Adresse"), {
            "fields": ("adresse", "ville", "province", "pays")
        }),
        (_("Organisation"), {
            "fields": ("type_client", "nom_organisation", "responsable", "fonction", "nombre_personnes")
        }),
        (_("Description du besoin"), {
            "fields": ("description_besoin",)
        }),
        (_("Intervention souhaitée"), {
            "fields": ("adresse_intervention", "ville_intervention", "province_intervention", "pays_intervention", "date_souhaitee", "niveau_urgence")
        }),
        (_("Contact & Origine"), {
            "fields": ("mode_contact_prefere", "source_demande", "piece_jointe")
        }),
        (_("Traitement administratif"), {
            "fields": ("statut", "commentaire_admin", "traite_par", "date_traitement")
        }),
        (_("PDF / Audit"), {
            "fields": ("pdf_preview", "pdf_genere", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    # Actions to update statut using values defined in the model
    @admin.action(description=_("Marquer comme 'En étude'"))
    def action_en_etude(self, request, queryset):
        updated = queryset.update(statut="en_etude")
        messages.success(request, _("%d demande(s) mise(s) en étude.") % updated)

    @admin.action(description=_("Marquer comme 'Contacté'"))
    def action_contacte(self, request, queryset):
        updated = queryset.update(statut="contacte")
        messages.success(request, _("%d demande(s) marquée(s) comme contactées.") % updated)

    @admin.action(description=_("Marquer comme 'Devis envoyé'"))
    def action_devis_envoye(self, request, queryset):
        updated = queryset.update(statut="devis_envoye")
        messages.success(request, _("%d demande(s) marquée(s) comme devis envoyé.") % updated)

    @admin.action(description=_("Marquer comme 'Acceptée'"))
    def action_acceptee(self, request, queryset):
        updated = queryset.update(statut="acceptee")
        messages.success(request, _("%d demande(s) acceptée(s).") % updated)

    @admin.action(description=_("Marquer comme 'Terminée'"))
    def action_terminee(self, request, queryset):
        updated = queryset.update(statut="terminee")
        messages.success(request, _("%d demande(s) marquée(s) comme terminées.") % updated)

    actions = (
        "action_en_etude",
        "action_contacte",
        "action_devis_envoye",
        "action_acceptee",
        "action_terminee",
    )
