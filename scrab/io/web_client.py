import requests
from typing import Optional


def load_page(url: str) -> Optional[str]:
    try:
        response = requests.get(url)
        response.raise_for_status()

        return response.text

    except requests.HTTPError as err:
        print(err)
        return None
