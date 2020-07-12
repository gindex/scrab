from typing import Optional

from scrab.formatter import to_text
from scrab.io.web_client import load_page
from scrab.parser import parse


def scrape(url: str) -> Optional[str]:
    # 1. load page
    page = load_page(url)
    if page is None:
        return None

    # 2. parse/extract content
    content_tree = parse(page)
    if content_tree is None:
        return None

    # 3. produce target format
    # TODO add markdown support
    content = to_text(content_tree)

    return content
