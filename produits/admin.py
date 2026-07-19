from django.contrib import admin

# Register your models here.
"""
produits.admin

Administration pour les modèles produits. Utilise uniquement les champs réels
définis dans produits/models.py et la fondation d'admin fournie par core.

ModelAdmins fournis :
 - ProduitAdmin
 - ProduitMediaAdmin
 - DemandeProduitAdmin

Respect strict : pas d'invention de champs, pas de placeholders, pas de
modification des mixins ou des modèles.
"""

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

from .models import Produit, ProduitMedia, DemandeProduit


# -----------------------------------------------------------------------------
# Inline: ProduitMediaInline
# -----------------------------------------------------------------------------
class ProduitMediaInline(ImagePreviewMixin, PDFPreviewMixin, admin.StackedInline):
    """
    Inline used on Produit edit page to add/edit media.
    StackedInline chosen because media records include files and descriptions.
    """
    model = ProduitMedia
    extra = 1
    fields = (
        "type_media",
        "titre_fr",
        "titre_en",
        "image",
        "video_url",
        "document",
        "ordre",
        "est_principal",
    )
    readonly_fields = ("image_preview", "pdf_preview")
    show_change_link = True
    ordering = ("ordre",)


# -----------------------------------------------------------------------------
# ProduitAdmin
# -----------------------------------------------------------------------------
@admin.register(Produit)
class ProduitAdmin(
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
    Admin for Produit.

    Uses only real fields from produits.models. Exposes inline media editing,
    search, filters, and performance optimizations via list_select_related.
    """

    show_full_result_count = True

    # Explicit list_display using fields that exist on Produit
    list_display = (
        "image_preview",
        "reference",
        "nom_fr",
        "nom_en",
        "categorie",
        "marque",
        "modele",
        "prix",
        "disponible",
        "badge",
        "est_actif",
        "mise_en_avant",
        "ordre_affichage",
        "date_publication",
    )

    # Filters: using only real fields
    list_filter = ("categorie", "badge", "etat", "disponible", "est_actif", "mise_en_avant")

    # Search across fields present on the model
    search_fields = ("reference", "nom_fr", "nom_en", "marque", "modele", "description_fr", "description_en")

    # Ordering: model.Meta defines ordering but we can provide admin default
    ordering = ("-mise_en_avant", "ordre_affichage", "nom_fr")

    # Performance: follow FK to categorie (and other FKs if shown) to avoid N+1
    list_select_related = ("categorie",)

    # Autocomplete for categorie — requires core.CategorieAdmin to define search_fields.
    # In this project core.admin was implemented with search_fields on Categorie, so autocomplete is safe.
    autocomplete_fields = ("categorie",)

    # Many-to-many services: use filter_horizontal for better UX
    filter_horizontal = ("services",)

    # Prepopulate slugs from names (fields exist: slug_fr, slug_en)
    prepopulated_fields = {"slug_fr": ("nom_fr",), "slug_en": ("nom_en",)}

    # Readonly preview fields (timestamps are added by TimestampAdminMixin)
    readonly_fields = ("image_preview", "pdf_preview")

    # Inlines: include media inline for direct editing on product page
    inlines = (ProduitMediaInline,)

    # Date hierarchy: show if date_publication exists (it does)
    date_hierarchy = "date_publication"

    # Fieldsets grouped by theme — only use fields that exist on the model
    fieldsets = (
        (_("Informations générales"), {
            "fields": ("reference", ("nom_fr", "nom_en"), ("slug_fr", "slug_en"), "categorie"),
        }),
        (_("Présentation"), {
            "fields": ("description_fr", "description_en", "image_principale", "brochure_pdf", "video_presentation"),
        }),
        (_("Informations commerciales"), {
            "fields": ("marque", "modele", "etat", ("prix", "disponible", "quantite_stock")),
        }),
        (_("Services associés"), {
            "fields": ("services",),
        }),
        (_("Personnalisation"), {
            "fields": ("icone", "couleur", "garantie", "reference_fournisseur"),
        }),
        (_("SEO"), {
            "fields": ("meta_title_fr", "meta_title_en", "meta_description_fr", "meta_description_en"),
            "classes": ("collapse",),
        }),
        (_("Publication"), {
            "fields": ("est_actif", "mise_en_avant", "ordre_affichage", "date_publication"),
        }),
        (_("Audit"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


# -----------------------------------------------------------------------------
# ProduitMediaAdmin
# -----------------------------------------------------------------------------
@admin.register(ProduitMedia)
class ProduitMediaAdmin(
    TimestampAdminMixin,
    ImagePreviewMixin,
    PDFPreviewMixin,
    AdminActionsMixin,
    BaseAdmin,
):
    """
    Admin for ProduitMedia. Also editable inline on Produit.
    """

    show_full_result_count = True

    list_display = ("image_preview", "titre_fr", "titre_en", "type_media", "ordre", "est_principal")
    list_filter = ("type_media", "est_principal")
    search_fields = ("titre_fr", "titre_en", "description_fr", "description_en")
    ordering = ("ordre",)

    # Optimize: when showing the product relation, avoid N+1
    list_select_related = ("produit",)

    readonly_fields = ("image_preview", "pdf_preview")

    fieldsets = (
        (None, {"fields": ("produit", "type_media", ("titre_fr", "titre_en"))}),
        (_("Description"), {"fields": ("description_fr", "description_en")}),
        (_("Fichiers"), {"fields": ("image", "video_url", "document")}),
        (_("Affichage"), {"fields": ("ordre", "est_principal")}),
        (_("Audit"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


# -----------------------------------------------------------------------------
# DemandeProduitAdmin
# -----------------------------------------------------------------------------
@admin.register(DemandeProduit)
class DemandeProduitAdmin(TimestampAdminMixin, PDFPreviewMixin, BaseAdmin):
    """
    Admin for DemandeProduit.
    """

    show_full_result_count = True

    list_display = (
        "produit",
        "nom",
        "prenom",
        "telephone",
        "email",
        "quantite",
        "demander_installation",
        "statut",
        "created_at",
    )

    list_filter = ("statut", "mode_contact_prefere", "demander_installation")
    search_fields = ("nom", "postnom", "prenom", "email", "telephone", "nom_organisation")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    # Optimize queries
    # Use list_select_related to avoid N+1 on these foreign keys
    list_select_related = ("produit", "service_souhaite", "traite_par")

    # Autocomplete fields:
    # - 'produit' autocomplete is safe because ProduitAdmin defines search_fields.
    # - 'service_souhaite' autocomplete is safe if ServiceAdmin defines search_fields.
    # If those admins did not provide search_fields, Django would raise validation error.
    # To remain performant and safe, we use autocomplete_fields for produit and service_souhaite.
    autocomplete_fields = ("produit", "service_souhaite")

    # For traite_par (AUTH_USER_MODEL), use raw_id_fields to avoid depending on UserAdmin search_fields.
    raw_id_fields = ("traite_par",)

    # PDFPreviewMixin expects pdf_field_name to point to the correct file field.
    pdf_field_name = "pdf_file"
    readonly_fields = ("pdf_preview", "pdf_genere", "date_traitement")

    fieldsets = (
        (_("Informations personnelles"), {"fields": (("nom", "postnom", "prenom"), ("telephone", "email"))}),
        (_("Adresse"), {"fields": ("adresse", "ville", "province", "pays")}),
        (_("Organisation / Client"), {"fields": ("type_client", "nom_organisation", "responsable")}),
        (_("Commande"), {"fields": ("quantite", "demander_installation", "service_souhaite")}),
        (_("Description"), {"fields": ("commentaire_client",)}),
        (_("Contact"), {"fields": ("mode_contact_prefere",)}),
        (_("Traitement administratif"), {"fields": ("statut", "commentaire_admin", "traite_par", "date_traitement")}),
        (_("PDF / Audit"), {"fields": ("pdf_preview", "pdf_genere", "created_at", "updated_at"), "classes": ("collapse",)}),
    )

    # Actions matching STATUT_CHOICES values exactly:
    @admin.action(description=_("Marquer comme 'Nouvelle'"))
    def action_nouvelle(self, request, queryset):
        updated = queryset.update(statut="nouvelle")
        messages.success(request, _("%d demande(s) marquée(s) comme 'Nouvelle'.") % updated)

    @admin.action(description=_("Marquer comme 'Contactée'"))
    def action_contactee(self, request, queryset):
        updated = queryset.update(statut="contacte")
        messages.success(request, _("%d demande(s) marquée(s) comme 'Contactée'.") % updated)

    @admin.action(description=_("Marquer comme 'Confirmée'"))
    def action_confirmee(self, request, queryset):
        updated = queryset.update(statut="confirmee")
        messages.success(request, _("%d demande(s) marquée(s) comme 'Confirmée'.") % updated)

    @admin.action(description=_("Marquer comme 'Livrée'"))
    def action_livree(self, request, queryset):
        updated = queryset.update(statut="livree")
        messages.success(request, _("%d demande(s) marquée(s) comme 'Livrée'.") % updated)

    @admin.action(description=_("Marquer comme 'Annulée'"))
    def action_annulee(self, request, queryset):
        updated = queryset.update(statut="annulee")
        messages.success(request, _("%d demande(s) marquée(s) comme 'Annulée'.") % updated)

    actions = ("action_nouvelle", "action_contactee", "action_confirmee", "action_livree", "action_annulee")
