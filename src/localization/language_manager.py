import logging
import pathlib
import json
from nicegui.elements import label
from nicegui import ui


class LabelMeta(type):
    """
    Metaclass to determine if an instance conforms to the class.

    This simplifies the logic to determine if an instance is a LabelElement.
    """

    def __instancecheck__(cls, instance):
        # Custom logic to determine if an instance conforms to the class
        return hasattr(instance, "_props") and "label" in instance._props


class LabelElement(metaclass=LabelMeta):
    """
    Class to determine if an instance is a LabelElement.

    This simplifies the logic to determine if an instance is a LabelElement.
    """

    _props: dict

    def update():
        pass


available_languages = set()


def load_localization_data():
    """
    Load the localization data from the localization files.

    This function loads the localization data from the localization files and returns it as a dictionary.
    Each file is a JSON file with the language as the filename stem. The combined data is returned as a nested dictionary with the key as the first level and the language as the second level.

    To help spot missing translations, the dictionary also contains a "XX" language. This replaces the text with Xs (and Ys for options in select elements). This is meant for development only
    """
    folder = pathlib.Path("src/localization/texts")
    data = {}
    for lang_file in folder.glob("*.json"):
        language = lang_file.stem
        available_languages.add(language)
        for key, translation in json.loads(
            lang_file.read_text(encoding="utf-8")
        ).items():
            data[key] = (
                data.get(key, {})
                | {language: translation}
                | {
                    "XX": "X" * len(translation)
                    if isinstance(translation, str)
                    else ["Y" * len(t) for t in translation]
                }
            )
    return data


localizations = load_localization_data()

localized_components: list[tuple[label.TextElement | LabelElement, dict[str, str]]] = []
current_language: str = "en"


def _localize_as_text(
    component: label.TextElement,
    localizations: dict[str, str],
    language: str | None = None,
):
    component.text = localizations.get(
        language or current_language, localizations.get("en", "UNKNOWN")
    )
    component.update()


def _localize_as_label(
    component: LabelElement, localizations: dict[str, str], language: str | None = None
):
    component._props["label"] = localizations.get(
        language or current_language, localizations.get("en", "UNKNOWN")
    )
    component.update()


def _localize_as_select(
    component: ui.select,
    localizations: dict[str, str],
    option_localizations: dict[str, list[str]],
    language: str | None = None,
):
    component._props["label"] = localizations.get(
        language or current_language, localizations.get("en", "UNKNOWN")
    )
    value_idx = component.options.index(component.value)
    component.options = option_localizations.get(
        language or current_language, option_localizations.get("en", [])
    )
    component.value = component.options[value_idx]
    component.update()


def get_available_languages():
    """Get the available languages"""
    return available_languages


def get_localization(key: str, language: str | None = None):
    """Get a localized string"""
    return localizations.get(key, {}).get(
        language or current_language, localizations.get(key, {}).get("en", "UNKNOWN")
    )


def make_localisable(
    component: label.TextElement | LabelElement,
    component_localizations: dict[str, str] = None,
    key: str = None,
    option_localizations: dict[str, list[str]] = None,
    options_key: str = None,
    language: str | None = None,
):
    """
    Register a component for localization.

    The type of the component is inferred. component_localizations are overwritten by the localizations for the key.
    If you need to translate the options of a ui.select element provide option_localizations and/or options_key.
    """
    component_localizations = (component_localizations or {}) | localizations.get(
        key, {}
    )
    if options_key:
        option_localizations = (option_localizations or {}) | localizations.get(
            options_key, {}
        )
    localized_components.append(
        (component, component_localizations, option_localizations)
    )
    if isinstance(component, label.TextElement):
        _localize_as_text(component, component_localizations, language)
    elif isinstance(component, ui.select) and option_localizations:
        _localize_as_select(
            component, component_localizations, option_localizations, language
        )
    elif isinstance(component, LabelElement):
        _localize_as_label(component, component_localizations, language)
    else:
        raise ValueError(f"Unsupported component type {type(component)}")


def unregister(component: label.TextElement | LabelElement):
    global localized_components
    localized_components = [
        comp for comp, _, _ in localized_components if comp != component
    ]


def set_language(lang: str):
    """Set the language for all registered components"""
    global current_language
    current_language = lang
    remove = []
    for component, localizations, option_localizations in localized_components:
        try:
            if isinstance(component, label.TextElement):
                _localize_as_text(component, localizations)
            elif isinstance(component, ui.select) and option_localizations:
                _localize_as_select(component, localizations, option_localizations)
            elif isinstance(component, LabelElement):
                _localize_as_label(component, localizations)
        except Exception as e:
            logging.debug(f"Error setting text for {component} {e}")
            remove.append(component)
    for component in remove:
        unregister(component)
