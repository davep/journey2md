"""Main utility code."""

##############################################################################
# Python imports.
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from datetime import datetime
from json import loads
from pathlib import Path
from typing import Any

##############################################################################
# Timezime help.
from pytz import timezone

##############################################################################
@dataclass
class Journey:
    """A Journey entry."""

    id: str
    """The ID of the entry."""
    date_journal: int
    """The date/time of the journal entry."""
    date_modified: int
    """The date/time the journal entry was last modified."""
    timezone: str
    """The timezone of the entry."""
    text: str
    """The text of the journal entry."""
    preview_text: str
    """The preview text of the journal entry."""
    mood: int
    """The mood value of the journal entry."""
    lat: float
    """The latitude of the journal entry."""
    lon: float
    """The longitude of the journal entry."""
    address: str
    """The address of the journal entry."""
    label: str
    """The label for the journal entry."""
    folder: str
    """The folder for the journal entry."""
    sentiment: float
    """The sentiment of the journal entry."""
    favourite: bool
    """Is this journal entry a favourite?"""
    music_title: str
    """The music title associated with this journal entry."""
    music_artist: str
    """The music artist associated with this journal entry."""
    photos: list[str]
    """The photos associated with this journal entry."""
    weather: dict[str, Any]
    """The details of the weather associated with this journal entry."""
    tags: list[str]
    """The tags associated with this journal entry."""
    type: str
    """The type of the text in this journal entry."""

    @property
    def journal_time(self) -> datetime:
        """The time of the journal entry."""
        return datetime.fromtimestamp(self.date_journal/1000, timezone(self.timezone or "UTC"))

    @property
    def modified_time(self) -> datetime:
        """The time of the journal entry was last modified."""
        return datetime.fromtimestamp(self.date_modified/1000, timezone(self.timezone or "UTC"))

    @property
    def markdown_file(self) -> Path:
        """The path to the Markdown file that should be made for this journal."""
        return Path(self.journal_time.strftime("%Y/%m/%d/%Y-%m-%d-%H-%M-%S-%f-%Z.md"))

##############################################################################
def get_args() -> Namespace:
    """Get the command line arguments.

    Returns:
        The command line arguments.
    """
    parser = ArgumentParser(
        prog="journey2md",
        description="A tool for converting a Journey export file into a daily-note Markdown collection",
    )

    parser.add_argument("journey_files", help="The directory that contains the unzipped Journey export")
    parser.add_argument("target_directory", help="The directory where the Markdown files will be created")

    return parser.parse_args()

##############################################################################
def export(journey: Path, daily: Path) -> None:
    """Export the Journey files to Markdown-based daily notes.

    Args:
        journey: The source Journey location.
        daily: The target daily location.
    """
    for source in journey.glob("*.json"):
        entry = Journey(**loads(source.read_text()))
        markdown = daily / entry.markdown_file
        print(markdown)

##############################################################################
def main() -> None:
    """Main entry point for the utility."""
    arguments = get_args()
    if not (journey := Path(arguments.journey_files)).is_dir():
        print("Journey source needs to be a directory")
        exit(1)
    if not (daily := Path(arguments.target_directory)).is_dir():
        print("The target needs to be an existing directory")
        exit(1)
    export(journey, daily)

##############################################################################
if __name__ == "__main__":
    main()

### __main__.py ends here
