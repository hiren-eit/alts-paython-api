import os 
from typing import Dict, Union
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel
from src.core.lifespan import lifespan
from src.core.settings import settings
from src.infrastructure.logging.logger_manager import setup_logging
from src.api.routes import file_manager_routes, file_activity_routes, account_master_routes, auth_routes, file_configuration_routes, account_details_routes
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
<div class="renderedMarkdown"><h1>Frame API Documentation</h1>
<br/>
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
    redoc_url="/redoc"
)

app.mount("/static", StaticFiles(directory="src/static"), name="static")

@app.get("/swagger", include_in_schema=False)
async def custom_swagger_ui_html():
    return HTMLResponse(content=f"""
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

<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="position:absolute;width:0;height:0">
  <defs>
    <symbol viewBox="0 0 20 20" id="unlocked">
      <path d="M15.8 8H14V5.6C14 2.703 12.665 1 10 1 7.334 1 6 2.703 6 5.6V6h2v-.801C8 3.754 8.797 3 10 3c1.203 0 2 .754 2 2.199V8H4c-.553 0-1 .646-1 1.199V17c0 .549.428 1.139.951 1.307l1.197.387C5.672 18.861 6.55 19 7.1 19h5.8c.549 0 1.428-.139 1.951-.307l1.196-.387c.524-.167.953-.757.953-1.306V9.199C17 8.646 16.352 8 15.8 8z"></path>
    </symbol>

    <symbol viewBox="0 0 20 20" id="locked">
      <path d="M15.8 8H14V5.6C14 2.703 12.665 1 10 1 7.334 1 6 2.703 6 5.6V8H4c-.553 0-1 .646-1 1.199V17c0 .549.428 1.139.951 1.307l1.197.387C5.672 18.861 6.55 19 7.1 19h5.8c.549 0 1.428-.139 1.951-.307l1.196-.387c.524-.167.953-.757.953-1.306V9.199C17 8.646 16.352 8 15.8 8zM12 8H8V5.199C8 3.754 8.797 3 10 3c1.203 0 2 .754 2 2.199V8z"/>
    </symbol>

    <symbol viewBox="0 0 20 20" id="close">
      <path d="M14.348 14.849c-.469.469-1.229.469-1.697 0L10 11.819l-2.651 3.029c-.469.469-1.229.469-1.697 0-.469-.469-.469-1.229 0-1.697l2.758-3.15-2.759-3.152c-.469-.469-.469-1.228 0-1.697.469-.469 1.228-.469 1.697 0L10 8.183l2.651-3.031c.469-.469 1.228-.469 1.697 0 .469.469.469 1.229 0 1.697l-2.758 3.152 2.758 3.15c.469.469.469 1.229 0 1.698z"/>
    </symbol>

    <symbol viewBox="0 0 20 20" id="large-arrow">
      <path d="M13.25 10L6.109 2.58c-.268-.27-.268-.707 0-.979.268-.27.701-.27.969 0l7.83 7.908c.268.271.268.709 0 .979l-7.83 7.908c-.268.271-.701.27-.969 0-.268-.269-.268-.707 0-.979L13.25 10z"/>
    </symbol>

    <symbol viewBox="0 0 20 20" id="large-arrow-down">
      <path d="M17.418 6.109c.272-.268.709-.268.979 0s.271.701 0 .969l-7.908 7.83c-.27.268-.707.268-.979 0l-7.908-7.83c-.27-.268-.27-.701 0-.969.271-.268.709-.268.979 0L10 13.25l7.418-7.141z"/>
    </symbol>

    <symbol viewBox="0 0 24 24" id="jump-to">
      <path d="M19 7v4H5.83l3.58-3.59L8 6l-6 6 6 6 1.41-1.41L5.83 13H21V7z"/>
    </symbol>

    <symbol viewBox="0 0 24 24" id="expand">
      <path d="M10 18h4v-2h-4v2zM3 6v2h18V6H3zm3 7h12v-2H6v2z"/>
    </symbol>

  </defs>
</svg>

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
<style>
  .swagger-ui .topbar .download-url-wrapper {{ display: none }}
</style>
</body>

</html>
""")

app.include_router(auth_routes.router)
app.include_router(file_manager_routes.router, dependencies=[Depends(get_current_user)])
app.include_router(business_rule_controller.router, dependencies=[Depends(get_current_user)])
app.include_router(file_activity_routes.router, dependencies=[Depends(get_current_user)])
app.include_router(account_master_routes.router, dependencies=[Depends(get_current_user)])
app.include_router(file_router_controller.router, dependencies=[Depends(get_current_user)])
app.include_router(file_configuration_routes.router, dependencies=[Depends(get_current_user)])
app.include_router(account_details_routes.router, dependencies=[Depends(get_current_user)])

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
        "status": "running"
    }
@app.get("/health", response_model=Dict[str, str])
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring and load balancers.
    Returns:
        Dict with health status indicator
    """
    return {"status": "healthy"}