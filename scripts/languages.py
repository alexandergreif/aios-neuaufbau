"""Central language table for the shared AIOS scripts.

An installation uses exactly one language. The table maps each language code to
its source folder, runtime root, package file names, private file names and the
texts that scripts write into language-specific files. Scripts never hardcode
these values. Technical files inside the state folder (installation.json,
bestand.json, betrieb.lock, sicherungen/, operation.json) keep their names in
every language.
"""

from dataclasses import dataclass
from pathlib import Path
import re


DEFAULT = "de"
CODES = ("de", "en")
PROFILE_KEYS = ("name_anrede", "rolle", "sprache", "zeitzone", "arbeitszeiten", "arbeitsweise", "prioritaeten")
STATUS_KEYS = ("active", "paused", "archived", "to_assign")


class LanguageError(ValueError):
    """Unknown or invalid language value."""


@dataclass(frozen=True, eq=False)
class Language:
    code: str
    source: str
    root: str
    core: str
    references: str
    skills: str
    profile_template: str
    register_template: str
    knowledge_index_template: str
    template_files: tuple
    template_dirs: tuple
    config_template: str
    client_test_references: tuple
    config_name: str
    profile_name: str
    register_name: str
    knowledge_dir: str
    state_dir: str
    register_header: tuple
    status_labels: tuple
    profile_labels: tuple
    open: str
    profile_status_template: str
    profile_status_done: str
    confirmed_label: str
    profile_title: str
    field_header: tuple
    preferences_heading: str
    preferences_header: tuple
    changes_heading: str
    transfer_status: str
    transfer_no_changes: str
    generated_from: str
    local_config_label: str
    profile_link_label: str
    manual_skill: str

    @property
    def core_path(self):
        """Core rules relative to the runtime and as manifest path."""
        return f"{self.root}/{self.core}"

    @property
    def references_path(self):
        return f"{self.root}/{self.references}"

    @property
    def skills_path(self):
        return f"{self.root}/{self.skills}"

    @property
    def core_link_prefix(self):
        """Relative link prefix used inside the core rules for references."""
        return f"../{self.references}/"

    @property
    def statuses(self):
        return dict(zip(STATUS_KEYS, self.status_labels))

    @property
    def status_values(self):
        return set(self.status_labels)

    @property
    def labels(self):
        """Profile field labels keyed by internal profile key."""
        return dict(zip(PROFILE_KEYS, self.profile_labels))

    def runtime_path(self, relative):
        return f"{self.root}/{relative}"

    def generated_header(self, digest):
        return f"<!-- {self.generated_from} {self.core_path}. SHA256: {digest} -->\n\n"

    def rewrite_core_links(self, text, replace):
        """Replace every Markdown link `](../<references>/<name>)` via replace(name)."""
        pattern = r"\]\(" + re.escape(self.core_link_prefix) + r"([^\)]+)\)"
        return re.sub(pattern, lambda match: "]" + replace(match.group(1)), text)

    def private_names(self):
        return (self.config_name, self.profile_name, self.register_name,
                f"{self.knowledge_dir}/INDEX.md", ".env")


GERMAN = Language(
    code="de", source="de", root="allgemein", core="regeln/kern.md", references="referenzen",
    skills="skills",
    profile_template="vorlagen/profil.md", register_template="vorlagen/projekte.md",
    knowledge_index_template="vorlagen/wissen/INDEX.md",
    template_files=("vorlagen/profil.md", "vorlagen/projekte.md", "vorlagen/wissen/INDEX.md",
                    "vorlagen/wissen/notiz.md", "vorlagen/projekt/PLAN.md", "vorlagen/projekt/NOTIZEN.md"),
    template_dirs=("vorlagen/wissen", "vorlagen/projekt"),
    config_template="konfiguration/pfade.vorlage.json",
    client_test_references=("externes-schreiben.md", "profil-und-wissen.md"),
    config_name="pfade.json", profile_name="profil.md", register_name="projekte.md",
    knowledge_dir="wissen", state_dir="zustand",
    register_header=("Kürzel", "Kunde oder Projekt", "Lokaler Ordner", "Repository", "Jira-Präfix", "Status"),
    status_labels=("aktiv", "pausiert", "archiviert", "zuordnen"),
    profile_labels=("Name und Anrede", "Rolle", "Sprache", "Zeitzone", "Arbeitszeiten und freie Tage",
                    "Arbeitsweise", "Prioritäten"),
    open="offen",
    profile_status_template="Status: noch nicht eingerichtet",
    profile_status_done="Status: eingerichtet",
    confirmed_label="Bestätigt am",
    profile_title="# Persönliches Profil",
    field_header=("Feld", "Bestätigter Wert"),
    preferences_heading="## Kleine Vorlieben",
    preferences_header=("Vorliebe", "Datum", "Grundlage"),
    changes_heading="## Bestätigte Änderungen",
    transfer_status="Status: übertragen, Angaben auf diesem Mac prüfen",
    transfer_no_changes="Keine Änderungen aus dem Quellprofil übertragen.",
    generated_from="Generiert aus",
    local_config_label="Lokale Konfiguration",
    profile_link_label="Profil",
    manual_skill="auftrag-vorbereiten",
)

ENGLISH = Language(
    code="en", source="en", root="general", core="rules/core.md", references="references",
    skills="skills",
    profile_template="templates/profile.md", register_template="templates/projects.md",
    knowledge_index_template="templates/knowledge/INDEX.md",
    template_files=("templates/profile.md", "templates/projects.md", "templates/knowledge/INDEX.md",
                    "templates/knowledge/note.md", "templates/project/PLAN.md", "templates/project/NOTES.md"),
    template_dirs=("templates/knowledge", "templates/project"),
    config_template="configuration/paths.template.json",
    client_test_references=("external-writes.md", "profile-and-knowledge.md"),
    config_name="paths.json", profile_name="profile.md", register_name="projects.md",
    knowledge_dir="knowledge", state_dir="state",
    register_header=("Key", "Customer or project", "Local folder", "Repository", "Jira prefix", "Status"),
    status_labels=("active", "paused", "archived", "to-assign"),
    profile_labels=("Name and form of address", "Role", "Language", "Time zone", "Working hours and days off",
                    "Working style", "Priorities"),
    open="open",
    profile_status_template="Status: not set up yet",
    profile_status_done="Status: set up",
    confirmed_label="Confirmed on",
    profile_title="# Personal profile",
    field_header=("Field", "Confirmed value"),
    preferences_heading="## Small preferences",
    preferences_header=("Preference", "Date", "Basis"),
    changes_heading="## Confirmed changes",
    transfer_status="Status: transferred, check the details on this Mac",
    transfer_no_changes="No changes transferred from the source profile.",
    generated_from="Generated from",
    local_config_label="Local configuration",
    profile_link_label="Profile",
    manual_skill="prepare-brief",
)

LANGUAGES = {"de": GERMAN, "en": ENGLISH}


def get(code):
    if not isinstance(code, str) or code not in LANGUAGES:
        raise LanguageError("language must be de or en.")
    return LANGUAGES[code]


def code_of_config(config):
    """Language code of a configuration object. A missing field means de."""
    if not isinstance(config, dict):
        raise LanguageError("Configuration must be an object.")
    return get(config.get("language", DEFAULT)).code


def of_config(config):
    return get(code_of_config(config))


def config_name_mismatch(config_path, profile, lang):
    """Explain a configuration whose file name belongs to the other language, otherwise None.

    The file name must match the language field: pfade.json for de, paths.json for en.
    """
    config_path, profile = Path(config_path), Path(profile)
    if config_path.parent != profile or config_path.name == lang.config_name:
        return None
    for other in LANGUAGES.values():
        if other is not lang and config_path.name == other.config_name:
            return (f"Configuration language {lang.code} does not match the file name {config_path.name}. "
                    f"Name the file {lang.config_name}, or keep {config_path.name} with "
                    f"\"language\": \"{other.code}\"")
    return None


def package_file(package, language, relative):
    """Path of a language file in a source checkout or, without it, in a runtime."""
    lang = get(language) if isinstance(language, str) else language
    source = package / lang.source
    base = source if source.is_dir() and not source.is_symlink() else package / lang.root
    return base / relative
