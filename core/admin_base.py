"""
core.admin_base
---------------

Base admin réutilisable pour le projet IT CENTER.

Fournit une classe BaseAdmin sûre et extensible pour tous les ModelAdmin du
projet. Les méthodes get_* vérifient l'existence des champs afin d'être
utilisables avec n'importe quel modèle sans provoquer d'erreurs.
"""

from django.contrib import admin
from django.core.exceptions import FieldDoesNotExist
from django.utils.translation import gettext_lazy as _


class BaseAdmin(admin.ModelAdmin):
    """
    Classe de base pour les ModelAdmin du projet.

    Comportement par défaut :
    - list_per_page = 25
    - save_on_top = True
    - save_as = True
    - readonly_fields inclut 'created_at' et 'updated_at' si présents sur le modèle
    - ordering par '-created_at' uniquement si le champ existe
    - date_hierarchy = 'created_at' uniquement si le champ existe
    - search_help_text = _("Rechercher...")
    """

    list_per_page = 25
    save_on_top = True
    save_as = True

    # Valeurs par défaut "souhaitées" — elles seront appliquées uniquement
    # si le modèle possède les champs correspondants.
    _default_ordering = ("-created_at",)
    _default_date_hierarchy = "created_at"

    # readonly_fields par défaut ; get_readonly_fields filtrera les champs
    # inexistants pour éviter les erreurs sur les modèles sans timestamp.
    readonly_fields = ("created_at", "updated_at")

    date_hierarchy = None  # accessible via get_date_hierarchy()
    search_help_text = _("Rechercher...")

    # ------------------------------------------------------------------
    # Helper utilitaire
    # ------------------------------------------------------------------
    def _model_has_field(self, field_name: str) -> bool:
        """
        Retourne True si le modèle lié au ModelAdmin expose `field_name`.
        Safe-fail : aucune exception n'est propagée.
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

    # ------------------------------------------------------------------
    # Méthodes personnalisables par les classes enfants
    # ------------------------------------------------------------------
    def get_ordering(self, request):
        """
        Retourne l'ordering appliqué pour cet admin.

        Si le modèle possède 'created_at', on retourne la valeur par défaut
        self._default_ordering. Sinon on retourne une liste vide (aucun
        ordering par défaut imposé).
        """
        # Respecter un éventuel ordering défini par l'enfant via attribut.
        parent_ordering = super().get_ordering(request)
        if parent_ordering:
            return parent_ordering

        if self._model_has_field("created_at"):
            return tuple(self._default_ordering)
        return ()

    def get_date_hierarchy(self, request):
        """
        Retourne le champ à utiliser pour date_hierarchy si présent.

        Renvoie 'created_at' uniquement si ce champ existe sur le modèle,
        sinon None (Django n'affichera pas de date_hierarchy).
        """
        if self._model_has_field(self._default_date_hierarchy):
            return self._default_date_hierarchy
        return None

    def get_readonly_fields(self, request, obj=None):
        """
        Retourne readonly_fields filtrés pour exclure tout champ absent sur
        le modèle (prévention d'erreurs si le modèle n'a pas created_at/updated_at).

        Amélioration : conserve également les noms qui correspondent à des
        attributs ou méthodes du ModelAdmin (par ex. image_preview fourni par
        un mixin). Cela évite de retirer les readonly_fields basés sur des
        méthodes d'affichage et prévient FieldError lors de l'utilisation de
        mixins additionnels.
        """
        readonly = list(super().get_readonly_fields(request, obj) or [])
        filtered = []
        for field in readonly:
            # 1) Si le modèle expose le champ → le conserver.
            # 2) Sinon, si le ModelAdmin (ou un mixin) possède un attribut/méthode
            #    de ce nom → le conserver (permet image_preview, pdf_preview, etc.).
            # 3) Sinon → le retirer.
            if self._model_has_field(field) or hasattr(self, field):
                filtered.append(field)
        return tuple(filtered)