from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("Marlin")

mcp.settings.transport_security.enable_dns_rebinding_protection = False

MARLIN_API = "http://127.0.0.1:8005"


@mcp.tool()
def describe_video(video_path: str):
    """
    Generate scene description and timeline.
    """

    with open(video_path, "rb") as f:

        response = requests.post(
            f"{MARLIN_API}/describe",
            files={
                "file": f
            },
            timeout=600
        )

    response.raise_for_status()

    return response.json()


@mcp.tool()
def search_video_event(
    video_path: str,
    query: str
):
    """
    Find when an event occurs.

    Example:
    - man raises his hands
    - train arrives
    - person enters room
    """

    with open(video_path, "rb") as f:

        response = requests.post(
            f"{MARLIN_API}/search",
            files={
                "file": f
            },
            data={
                "query": query
            },
            timeout=600
        )

    response.raise_for_status()

    return response.json()


app = mcp.streamable_http_app()
