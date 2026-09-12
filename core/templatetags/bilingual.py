from django import template
from django.utils.translation import get_language

register = template.Library()


@register.filter(name='bilingual')
def bilingual(obj, field_base_name):
    """
    Retourne la valeur du champ bilingue correspondant à la langue active.

    Utilisation dans un template :
        {{ apropos|bilingual:"titre" }}
        {{ domaine|bilingual:"description" }}

    Convention attendue sur l'objet : `<field_base_name>_fr` et `<field_base_name>_en`.

    Comportement :
      - utilise la langue active de Django (get_language()) pour choisir
        le champ `_fr` ou `_en` ;
      - si le champ de la langue active est vide/None, tente un fallback
        vers l'autre langue ;
      - si aucun des deux champs n'existe sur l'objet, retourne une chaîne vide ;
      - ne lève jamais d'exception côté template.
    """
    if obj is None or not field_base_name:
        return ''

    current_lang = get_language() or ''
    is_english = current_lang.startswith('en')

    field_fr = f'{field_base_name}_fr'
    field_en = f'{field_base_name}_en'

    # Valeurs récupérées prudemment : None si l'attribut n'existe pas sur l'objet.
    value_fr = getattr(obj, field_fr, None)
    value_en = getattr(obj, field_en, None)

    if is_english:
        primary, fallback = value_en, value_fr
    else:
        primary, fallback = value_fr, value_en

    if primary:
        return primary
    if fallback:
        return fallback
    return ''