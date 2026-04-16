from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
import uvicorn
import threading
from fastmcp import FastMCP
import httpx
import os
from typing import Optional

mcp = FastMCP("NCAA API")

BASE_URL = "https://ncaa-api.henrygd.me"


@mcp.tool()
async def get_scoreboard(
    sport: str,
    division: str,
    year: str,
    week_or_date: str,
    conference: str = "all-conf",
    page: int = 1
) -> dict:
    """Fetch live or recent scores for a given sport, division, and date.
    Use this when a user asks about current scores, game results, or wants to
    know who is playing on a specific date. The path mirrors ncaa.com scoreboard URLs.
    
    Examples:
    - Football FBS week 13 of 2023: sport='football', division='fbs', year='2023', week_or_date='13'
    - Basketball D1 on 11/15/2023: sport='basketball-men', division='d1', year='2023', week_or_date='11/15/2023'
    """
    url = f"{BASE_URL}/scoreboard/{sport}/{division}/{year}/{week_or_date}/{conference}"
    params = {"page": page}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_stats(
    sport: str,
    division: str,
    season: str,
    stat_type: str,
    category_id: str,
    page: int = 1
) -> dict:
    """Retrieve NCAA statistics for a sport and division, either team or individual stats.
    Use this when a user wants to see statistical leaders, team rankings by stat category,
    or individual player stats.
    
    stat_type must be either 'team' or 'individual'.
    category_id is a numeric string (e.g. '28' for rushing yards, '750' for individual passing).
    Use 'current' for the current season or a specific year for season.
    """
    url = f"{BASE_URL}/stats/{sport}/{division}/{season}/{stat_type}/{category_id}"
    params = {"page": page}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_rankings(
    sport: str,
    division: str,
    poll: str,
    page: int = 1
) -> dict:
    """Fetch current NCAA rankings for a sport and division from a specific poll or ranking system.
    Use this when a user wants to see poll rankings, AP top 25, coaches poll, or other ranking systems.
    
    Examples:
    - AP Top 25 football: sport='football', division='fbs', poll='associated-press'
    - Coaches poll: poll='coaches'
    - Women's basketball RPI: sport='basketball-women', division='d1', poll='ncaa-womens-basketball-rpi'
    """
    url = f"{BASE_URL}/rankings/{sport}/{division}/{poll}"
    params = {"page": page}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_standings(
    sport: str,
    division: str,
    page: int = 1
) -> dict:
    """Retrieve conference standings for a sport and division.
    Use this when a user wants to see win-loss records, conference standings,
    or how teams rank within their conference.
    
    Examples:
    - Women's basketball D1: sport='basketball-women', division='d1'
    - FBS football: sport='football', division='fbs'
    """
    url = f"{BASE_URL}/standings/{sport}/{division}"
    params = {"page": page}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_game_info(game_id: str) -> dict:
    """Get general information about a specific NCAA game by its game ID.
    Use this as the starting point when a user asks about a particular game to get
    metadata like teams, date, venue, and final score.
    
    game_id is a numeric string found in ncaa.com game URLs (e.g. '6305900').
    """
    url = f"{BASE_URL}/game/{game_id}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_game_details(game_id: str, detail_type: str) -> dict:
    """Retrieve detailed data for a specific NCAA game.
    Use this when a user wants in-depth game analysis, individual player performance,
    or a full breakdown of how a game unfolded.
    
    detail_type options:
    - 'boxscore': player/team box score
    - 'play-by-play': sequence of plays
    - 'scoring-summary': scoring events only
    - 'team-stats': aggregated team statistics
    
    game_id is a numeric string (e.g. '6305900').
    """
    valid_detail_types = {"boxscore", "play-by-play", "scoring-summary", "team-stats"}
    if detail_type not in valid_detail_types:
        return {
            "error": f"Invalid detail_type '{detail_type}'. Must be one of: {', '.join(sorted(valid_detail_types))}"
        }
    url = f"{BASE_URL}/game/{game_id}/{detail_type}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_schedule(path: str, page: int = 1) -> dict:
    """Fetch the schedule of games for a specific team or sport.
    Use this when a user wants to know upcoming or past games for a team,
    including dates, opponents, and results.
    
    The path parameter should be the schedule path segment as used on ncaa.com.
    Examples:
    - Football uses year only: 'football/fbs/alabama/2023'
    - Basketball uses year/month: 'basketball-men/d1/2023/02'
    """
    # Strip leading slash if present
    path = path.lstrip("/")
    url = f"{BASE_URL}/schedule/{path}"
    params = {"page": page}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_bracket(path: str, page: int = 1) -> dict:
    """Retrieve NCAA tournament bracket data including matchups, results, and advancement.
    Use this when a user asks about March Madness, tournament brackets, or playoff structures.
    
    The path parameter mirrors the ncaa.com bracket page path.
    Examples:
    - Men's basketball 2023: 'basketball-men/d1/2023'
    - Women's basketball 2024: 'basketball-women/d1/2024'
    
    Note: FBS football brackets are only available from 2025 onwards.
    """
    # Strip leading slash if present
    path = path.lstrip("/")
    url = f"{BASE_URL}/brackets/{path}"
    params = {"page": page}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()




_SERVER_SLUG = "henrygd-ncaa-api"

def _track(tool_name: str, ua: str = ""):
    try:
        import urllib.request, json as _json
        data = _json.dumps({"slug": _SERVER_SLUG, "event": "tool_call", "tool": tool_name, "user_agent": ua}).encode()
        req = urllib.request.Request("https://www.volspan.dev/api/analytics/event", data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=1)
    except Exception:
        pass

async def health(request):
    return JSONResponse({"status": "ok", "server": mcp.name})

async def tools(request):
    registered = await mcp.list_tools()
    tool_list = [{"name": t.name, "description": t.description or ""} for t in registered]
    return JSONResponse({"tools": tool_list, "count": len(tool_list)})

sse_app = mcp.http_app(transport="sse")

app = Starlette(
    routes=[
        Route("/health", health),
        Route("/tools", tools),
        Mount("/", sse_app),
    ],
    lifespan=sse_app.lifespan,
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
