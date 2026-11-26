# Wikipedia search
import requests


def search_wikipedia(query: str) -> str:
    """
    Search Wikipedia and return a short summary.
    """

    try:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/"

        response = requests.get(
            url + requests.utils.quote(query),
            headers={
                "User-Agent": "XION-Personal-AI/1.0"
            },
            timeout=10
        )

        if response.status_code == 404:
            return f"I couldn't find a Wikipedia page for '{query}'."

        response.raise_for_status()

        data = response.json()

        title = data.get("title", query)
        extract = data.get("extract")

        if not extract:
            return f"I couldn't find useful information about '{query}'."

        return f"Wikipedia result for {title}: {extract}"

    except requests.exceptions.RequestException as e:
        return f"Wikipedia connection failed: {e}"

    except Exception as e:
        return f"Wikipedia search failed: {e}"