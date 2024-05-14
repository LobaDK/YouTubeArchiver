from InquirerPy import inquirer
from InquirerPy.base import Choice

from lib.settings import Settings

"""
TODO:
1. Create a MenuBuilder class that can do the following:
    - Build a list of InquirerPy choices, based on current settings. The possible choices will be provided by another class.
    - Prompt the user with the choices, and return the user's selection.

2. Create a Menu class that act as the actual menu, doing the following:
    - Provides a list of choices for the MenuBuilder to use.
    - Handles the user's selection.

3. Some form of place to store the choices, how to handle each choice, and functions required for any choices, most likely a class for each menu.
"""


class ChoiceDependency:
    def __init__(self, required_settings: dict[str]):
        """
        Helper class that defines a set of settings that must be enabled for a choice to be shown.

        Args:
            required_settings (dict[str]): A dictionary of settings that must be enabled for the choice to be shown. The key is the setting name, and the value is the value that the setting must have.
        """
        self._required_settings = required_settings

    def is_satisfied(self, settings: Settings) -> bool:
        """
        Check if the required settings are enabled.

        Args:
            settings (Settings): The current settings.

        Returns:
            bool: True if all required settings are enabled, False otherwise.
        """

        def get_nested_attr(obj, attr_path):
            for attr in attr_path.split("."):
                obj = getattr(obj, attr)
            return obj

        return all(
            get_nested_attr(settings, setting) == value
            for setting, value in self._required_settings.items()
        )


class MenuBuilder:
    def __init__(
        self,
        choices: list[Choice],
        choice_dependencies: dict[str, ChoiceDependency],
    ):
        """
        Helper class that dynamically builds a list of InquirerPy choices based on the provided list of choices and settings.

        Args:
            choices (list[Choice]): A list of InquirerPy choices.
            choice_dependencies (dict[str, ChoiceDependency]): A dictionary of choice values and their required settings. The key is the choice value, and the value is a ChoiceDependency object that encapsulates the settings that must be satisfied for the choice to be shown.

        Notes:
            It is important that the value of the choice matches the key in the choice_dependencies dictionary.
        """
        self._choices = choices
        self._choice_dependencies = choice_dependencies

    def build_choices(self, settings: Settings) -> list[Choice]:
        """
        Build a list of InquirerPy choices based on the provided settings.

        Args:
            settings (Settings): The current settings.

        Returns:
            list[Choice]: A list of InquirerPy choices.
        """
        return [
            choice
            for choice in self._choices
            if self._choice_dependencies[choice.value].is_satisfied(settings)
        ]

    def prompt(self, settings: Settings) -> str:
        """
        Prompt the user with the choices, and return the user's selection.

        Args:
            settings (Settings): The current settings.

        Returns:
            str: The user's selection.
        """
        choices = self.build_choices(settings)
        return inquirer.select(
            message="Select an option:",
            choices=choices,
        ).execute()


class Menu:
    def __init__(
        self,
        settings: Settings,
        choices: list[Choice],
        choice_required_settings: dict[str, dict[str]],
    ):
        self._settings = settings
        self._choices = choices

        self._choice_dependencies = {
            choice.value: ChoiceDependency(
                choice_required_settings.get(choice.value, {})
            )
            for choice in choices
        }
        self._menu_builder = MenuBuilder(choices, self._choice_dependencies)

    def start(self):
        return self._menu_builder.prompt(self._settings)


class MainMenu:
    # TODO: Override Choice class and add custom "depends_on" dict attribute instead of this mess
    choices = [
        Choice(
            value="select_url",
            name="Select URL:",
        ),
        Choice(
            value="select_folder",
            name="Select Folder:",
        ),
        Choice(
            value="use_archive_file",
            name="Use Archive File:",
        ),
        Choice(
            value="select_archive_file",
            name="Select Archive File:",
        ),
    ]
    choice_required_settings = {
        "select_folder": {"url_is_set": False},
        "use_archive_file": {"url_is_set": False},
        "select_archive_file": {
            "url_is_set": False,
            "persistent.use_archive_file": True,
        },
    }
