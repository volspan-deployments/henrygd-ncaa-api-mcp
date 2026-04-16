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
    """Fetch live or historical scores for a given NCAA sport, division, and date.
    Use this when the user wants to know current scores, game results, or scheduled games for a specific sport and date.
    
    Args:
        sport: Sport slug as used on ncaa.com, e.g. 'football', 'basketball-men', 'basketball-women', 'baseball', 'soccer-men', 'soccer-women'
        division: Division or subdivision, e.g. 'fbs', 'fcs', 'd1', 'd2', 'd3'
        year: Four-digit year, e.g. '2023'
        week_or_date: Week number for football (e.g. '13') or date string for other sports (e.g. '11/18/2023')
        conference: Conference filter slug, e.g. 'all-conf', 'acc', 'sec', 'big-ten'. Defaults to 'all-conf'.
        page: Page number for paginated results. Defaults to 1.
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
    stat_category_id: str,
    page: int = 1
) -> dict:
    """Retrieve NCAA statistics for a sport and division, either team stats or individual player stats.
    Use this when the user asks about team or player performance metrics for a season.
    
    Args:
        sport: Sport slug as used on ncaa.com, e.g. 'football', 'basketball-men', 'baseball'
        division: Division, e.g. 'fbs', 'd1', 'd2', 'd3'
        season: Season identifier, typically 'current' or a specific year like '2023'
        stat_type: Either 'team' for team stats or 'individual' for player stats
        stat_category_id: Numeric ID for the stat category as found on ncaa.com, e.g. '28' for rushing yards, '750' for passing efficiency
        page: Page number for paginated results. Defaults to 1.
    """
    url = f"{BASE_URL}/stats/{sport}/{division}/{season}/{stat_type}/{stat_category_id}"
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
    """Fetch NCAA rankings for a sport, division, and poll/ranking system.
    Use this when the user wants to know the current or historical rankings for a team or sport.
    
    Args:
        sport: Sport slug as used on ncaa.com, e.g. 'football', 'basketball-men', 'basketball-women'
        division: Division, e.g. 'fbs', 'd1'
        poll: Poll or ranking system slug, e.g. 'associated-press', 'coaches', 'cfp'
        page: Page number for paginated results. Defaults to 1.
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
    """Retrieve NCAA standings for a sport and division, showing win/loss records and conference standings.
    Use this when the user wants to know how teams are ranked within their conferences or overall.
    
    Args:
        sport: Sport slug as used on ncaa.com, e.g. 'football', 'basketball-men', 'basketball-women', 'baseball'
        division: Division, e.g. 'd1', 'd2', 'd3', 'fbs', 'fcs'
        page: Page number for paginated results. Defaults to 1.
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
    Use this as the starting point when the user asks about a particular game, its teams, time, location, or outcome.
    
    Args:
        game_id: The NCAA game ID as found on ncaa.com game URLs, e.g. '6305900'
    """
    url = f"{BASE_URL}/game/{game_id}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_game_details(game_id: str, detail_type: str) -> dict:
    """Get detailed data for a specific NCAA game such as box score, play-by-play, scoring summary, or team stats.
    Use this when the user wants in-depth game analysis, specific plays, or statistical breakdowns of a game.
    
    Args:
        game_id: The NCAA game ID as found on ncaa.com game URLs, e.g. '6305900'
        detail_type: Type of detail to retrieve: 'boxscore' for box score stats, 'play-by-play' for all plays, 'scoring-summary' for scoring events only, or 'team-stats' for team-level statistics
    """
    valid_detail_types = ["boxscore", "play-by-play", "scoring-summary", "team-stats"]
    if detail_type not in valid_detail_types:
        return {
            "error": f"Invalid detail_type '{detail_type}'. Must be one of: {', '.join(valid_detail_types)}"
        }
    url = f"{BASE_URL}/game/{game_id}/{detail_type}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_schedule(
    sport: str,
    division: str,
    season: str,
    team_id: Optional[str] = None,
    page: int = 1
) -> dict:
    """Fetch the schedule for a specific NCAA team or sport for a given season.
    Use this when the user wants to know upcoming games, past results, or the full season schedule for a team.
    
    Args:
        sport: Sport slug as used on ncaa.com, e.g. 'football', 'basketball-men', 'baseball'
        division: Division, e.g. 'fbs', 'd1', 'd2', 'd3'
        season: Season year or identifier, e.g. '2023' or 'current'
        team_id: Optional team ID to filter schedule for a specific team, as found in ncaa.com URLs
        page: Page number for paginated results. Defaults to 1.
    """
    url = f"{BASE_URL}/schedule/{sport}/{division}/{season}"
    params = {"page": page}
    if team_id:
        params["team"] = team_id
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_bracket(
    sport: str,
    division: str,
    year: str,
    page: int = 1
) -> dict:
    """Retrieve tournament bracket data for NCAA championships.
    Use this when the user asks about March Madness, NCAA tournament brackets, or postseason tournament results and matchups.
    
    Args:
        sport: Sport slug as used on ncaa.com, e.g. 'basketball-men', 'basketball-women', 'baseball'
        division: Division, e.g. 'd1', 'd2', 'd3'
        year: Tournament year, e.g. '2023'
        page: Page number for paginated results. Defaults to 1.
    """
    url = f"{BASE_URL}/brackets/{sport}/{division}/{year}"
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
