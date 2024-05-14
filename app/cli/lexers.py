"""
app.cli.lexers
==============

Commands related to language syntax.
"""

from __future__ import annotations

import re
from pathlib import Path

import click
from flask.cli import with_appcontext


@click.group()
def lexers() -> None:
    """Commands related to language syntax."""


@lexers.command()
@with_appcontext
def readme() -> None:
    """Update all languages."""
    root = Path(__file__).parent.parent.parent
    markdown = root / ".github" / "LEXERS.md"
    highlight_js = root / "assets" / "js" / "highlight.js"
    languages = []
    for line in highlight_js.read_text(encoding="utf-8").splitlines():
        if line.startswith("hljs.registerLanguage("):
            match = re.match(
                r'hljs\.registerLanguage\("([a-zA-Z]+)", [a-zA-Z]+\);', line
            )
            if match is not None:
                languages.append(f"- {match.group(1)}\n")

    markdown.write_text(
        "# Languages\n\n{}".format("\n".join(sorted(languages))),
        encoding="utf-8",
    )
    print("readme written successfully")
