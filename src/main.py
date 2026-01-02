import os
from typing import Dict
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from src.core.lifespan import lifespan
from src.core.settings import settings
from src.infrastructure.logging.logger_manager import setup_logging
from src.api.routes import (
    file_manager_routes,
    file_activity_routes,
    account_master_routes,
    auth_routes,
    file_configuration_routes,
    validation_routes,
    master_configuration_type_routes,
    account_details_routes,
)
from src.api.controllers import business_rule_controller, file_router_controller
from src.core.security import get_current_user

# This reads config.ini and sets up console + active logger (db or app insights)
setup_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    description=r"""
<h1>Frame API Documentation</h1>
<h2>Getting Started</h2>
<p>Authentication and standard conventions for the Frame API.</p>
<p>We'll send you a secret link with the following information</p>
<ul>
<li>a Client ID</li>
<li>a Client Secret</li>
</ul>
<table>
<tbody>
<tr>
<td>
<h3>Getting Started</h3>
<p>To get started, you need to request credentials from us at <a href="/swagger">api-support@pcr.com</a>.</p>
</td>
</tr>
<tr>
<td>
<h3>Authentication</h3>
<p>To authenticate, you'll need to make a POST request to your authentication endpoint. Include your <b>Client ID</b> and <b>Client Secret</b> in the request body.</p>
<p>Using <a rel="noopener noreferrer" target="_blank" href="https://curl.se/">curl</a>, that request might look like this:</p>
<p><strong>Note:</strong> Tokens should be stored and reused until they expire.</p>
<p>You can find the expiration time by decoding the <a href="https://www.jwt.io/introduction">JWT</a>, and checking the <code>exp</code> field, which is the expiration time represented as seconds since the Unix Epoch.</p>
</td>
<td>
<pre><code>CLIENT_ID='<your client id>'
CLIENT_SECRET='<your client secret>'
curl -X 'POST' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d "{ \
    \"clientId\": \"$CLIENT_ID\", \
    \"clientSecret\": \"$CLIENT_SECRET\" \
  }" \
  'http://127.0.0.1:8000/auth/token'
</code></pre>
</td>
</tr>
<tr>
<td>
<h3>Querying</h3>
<p>Once you have an access token, you can query the API as described below. The authorization header should include your Access Token, prefixed by the word "Bearer". <code>(e.g. authorization: Bearer tokendata...)</code></p>
</td>
<td>
<pre><code>ACCESS_TOKEN='<access token from the previous step>'
curl -X 'GET' \
  'api_url' \
  -H 'accept: application/json' \
  -H "authorization: Bearer $ACCESS_TOKEN"
</code></pre>
</td>
</tr>
</tbody></table>
<h2>Core APIs</h2>
<table>
<tbody><tr>
<td>
<h3>File Manager</h3>
<p>Manage your file lifecycle. Upload files, track their status (To Review, Approved, Completed), and retrieve detailed metadata or extraction results for specific files using their Unique ID.</p>
<h3>Extraction & Business Rules</h3>
<p>Frame extracts data from files and validates it against your custom business rules. You can manage these rules via the API and retrieve extraction configurations for specific file types.</p>
<h3>Account Master</h3>
<p>Manage the underlying structural data of your organization, including firms and their associated accounts, providing the context needed for all file operations.</p>
<h3>File Routing & Logs</h3>
<p>Configure how files move through your workflows with File Router. Every milestone and modification is captured in the File Activity logs, ensuring a comprehensive audit trail.</p>
</td>
<td>
<img src="/static/images/workflow.png" width="400">
</td>
</tr>
</tbody></table>

<h2>Standards</h2>
<table>
<tbody><tr><td>
<h3>Time Zone</h3>
<p>All dates and times are handled in UTC and follow the ISO 8601 standard.</p>
</td>
</tr></tbody></table></div>""",
    docs_url=None,
    redoc_url="/redoc",
)

app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.include_router(auth_routes.router)
app.include_router(file_manager_routes.router, dependencies=[Depends(get_current_user)])
app.include_router(
    business_rule_controller.router, dependencies=[Depends(get_current_user)]
)
app.include_router(
    file_activity_routes.router, dependencies=[Depends(get_current_user)]
)
app.include_router(
    account_master_routes.router, dependencies=[Depends(get_current_user)]
)
app.include_router(
    file_router_controller.router, dependencies=[Depends(get_current_user)]
)
app.include_router(
    file_configuration_routes.router, dependencies=[Depends(get_current_user)]
)
app.include_router(validation_routes.router, dependencies=[Depends(get_current_user)])
app.include_router(
    master_configuration_type_routes.router, dependencies=[Depends(get_current_user)]
)
app.include_router(
    account_details_routes.router, dependencies=[Depends(get_current_user)]
)


@app.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, str]:
    """
    Root endpoint providing basic application information.
    Returns:
        Dict containing application name, version, and status
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health", response_model=Dict[str, str])
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring and load balancers.
    Returns:
        Dict with health status indicator
    """
    return {"status": "healthy"}


@app.get("/swagger", include_in_schema=False)
async def custom_swagger_ui_html():
    return HTMLResponse(
        content=f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{settings.app_name}</title>
  <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css" >
  <link rel="icon" href="/static/images/favicon.ico" />
  <style>
    html
    {{
      box-sizing: border-box;
      overflow: -moz-scrollbars-vertical;
      overflow-y: scroll;
    }}
    *,
    *:before,
    *:after
    {{
      box-sizing: inherit;
    }}

    body {{
      margin:0;
      background: #fafafa;
    }}
  </style>
</head>

<body>
<div id="swagger-ui"></div>

<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"> </script>
<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-standalone-preset.js"> </script>
<script>
window.onload = function() {{
  const ui = SwaggerUIBundle({{
    url: '{app.openapi_url}',
    dom_id: '#swagger-ui',
    presets: [
      SwaggerUIBundle.presets.apis,
      SwaggerUIStandalonePreset
    ],
    layout: "StandaloneLayout",
    deepLinking: true,
    showExtensions: true,
    showCommonExtensions: true,
  }});
  window.ui = ui;
}};
</script>
<script src='/static/scripts/custom.js'></script>

<link href='/static/css/custom.css' rel='stylesheet'>

</body>

</html>
"""
    )


# <style>
#   .swagger-ui .topbar .download-url-wrapper {{ display: none }}
# </style>
