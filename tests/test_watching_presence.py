"""Discord Watching presence shows the package version."""

from ultron import __version__
from ultron.bot import watching_presence_name


def test_watching_presence_name_includes_ultron_and_version() -> None:
    assert watching_presence_name() == f"Ultron v{__version__}"
    assert watching_presence_name("9.9.9") == "Ultron v9.9.9"
