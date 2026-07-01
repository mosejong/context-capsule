import re
from pathlib import Path


LOCAL_MD_LINK = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^)]+\.md(?:#[^)]+)?)\)")


def test_local_markdown_links_exist():
    broken = []

    for markdown_file in [Path("README.md"), Path("START_HERE_KO.md"), *Path("docs").rglob("*.md")]:
        text = markdown_file.read_text(encoding="utf-8")
        for match in LOCAL_MD_LINK.finditer(text):
            link = match.group(1).split("#", 1)[0]
            target = (markdown_file.parent / link).resolve()
            if not target.exists():
                broken.append(f"{markdown_file}:{match.start()} -> {link}")

    assert not broken, "Broken markdown links:\n" + "\n".join(broken)
