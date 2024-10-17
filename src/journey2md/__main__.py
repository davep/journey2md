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
# Markdownify imports.
from markdownify import markdownify  # type: ignore

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
        return datetime.fromtimestamp(
            self.date_journal / 1000, timezone(self.timezone or "UTC")
        )

    @property
    def modified_time(self) -> datetime:
        """The time of the journal entry was last modified."""
        return datetime.fromtimestamp(
            self.date_modified / 1000, timezone(self.timezone or "UTC")
        )

    @property
    def markdown_directory(self) -> Path:
        """The directory that this entry should be created in."""
        return Path(self.journal_time.strftime("%Y/%m/%d/"))

    @property
    def markdown_attachment_directory(self) -> Path:
        """The location of the attachment directory associated with this journal entry."""
        return self.markdown_directory / "attachments"

    @property
    def markdown_file(self) -> Path:
        """The path to the Markdown file that should be made for this journal."""
        return self.markdown_directory / Path(
            self.journal_time.strftime("%Y-%m-%d-%H-%M-%S-%f-%Z.md")
        )

    @property
    def _front_matter_tags(self) -> str:
        """The tags formatted for use in Markdown front matter."""
        return f"tags:\n  - {'\n  - '.join(self.tags)}" if self.tags else ""

    @property
    def _front_matter_icbm(self) -> str:
        """The ICBM location of the journal entry as Markdown front matter."""
        # Note the not-quite-right sanity checking here. If you are likely
        # to have been exactly in the bounding locations, adjust to taste. I
        # never have been.
        if 0 < self.lat <= 90 and -180 < self.lon <= 180:
            return f"latitude: {self.lat}\nlongitude: {self.lon}"
        return ""

    @property
    def _front_matter_weather(self) -> str:
        """The weather data for the journal entry as Markdown front matter."""
        # Assume that it's only worth including the weather if it has the
        # main values filled in.
        if (
            self.weather
            and self.weather["place"]
            and self.weather["icon"]
            and self.weather["description"]
        ):
            # Note that I've only ever used Journey as a user who works in
            # C, not F. I've no idea if the exported data always converts
            # the temperature to C or not. Adjust to taste.
            return (
                f"weather-degree-c: {self.weather['degree_c']}\n"
                f"weather-place: {self.weather['place']}\n"
                f"weather-description: {self.weather['description']}"
            )
        return ""

    @property
    def markdown(self) -> str:
        """The journey journal entry as a markdown document."""

        # Start with the front matter.
        front_matter = "\n".join(
            matter
            for matter in (
                f"journal-time: {self.journal_time}",
                f"modified-time: {self.modified_time}",
                f"timezone: {self.timezone}" if self.timezone else "",
                f"mood: {self.mood}",
                self._front_matter_icbm,
                f"label: {self.label}" if self.label else "",
                f"folder: {self.folder}" if self.folder else "",
                f"sentiment: {self.sentiment}",
                f"music-title: {self.music_title}" if self.music_title else "",
                f"music-artist: {self.music_artist}" if self.music_artist else "",
                self._front_matter_weather,
                self._front_matter_tags,
                f"original-type: {self.type if self.type else 'plain-text'}",
            )
            if matter
        )
        markdown = f"---\n{front_matter}\n---\n\n"

        # Add the title.
        markdown += f"# {self.journal_time.strftime('%A %B %-d %Y %X')}\n\n"

        # Add the body, depending on type.
        if self.type == "html":
            markdown += markdownify(self.text)
        else:
            markdown += self.text

        # If there are photos...
        if self.photos:
            markdown += "\n---\n" + "\n---\n".join(
                f"\n![[{photo}]]\n" for photo in self.photos
            )

        return markdown


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

    parser.add_argument(
        "journey_files", help="The directory that contains the unzipped Journey export"
    )
    parser.add_argument(
        "target_directory",
        help="The directory where the Markdown files will be created",
    )

    return parser.parse_args()


##############################################################################
def export(journey: Path, daily: Path) -> None:
    """Export the Journey files to Markdown-based daily notes.

    Args:
        journey: The source Journey location.
        daily: The target daily location.
    """
    for source in journey.glob("*.json"):
        # Get the entry from the Journey export.
        entry = Journey(**loads(source.read_text()))
        # Figure out the path to the output file.
        markdown = daily / entry.markdown_file
        # Ensure its directory exists so we can actually write the file.
        markdown.parent.mkdir(parents=True, exist_ok=True)
        markdown.write_text(entry.markdown)
        print(f"Exported {entry.journal_time}")
        # If the entry has photos too...
        if entry.photos:
            # ...copy them to the attachment directory.
            (attachments := (daily / entry.markdown_attachment_directory)).mkdir(
                parents=True, exist_ok=True
            )
            for photo in entry.photos:
                print(f"\tAttaching {photo}")
                (attachments / photo).write_bytes((journey / photo).read_bytes())


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
