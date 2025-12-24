
API_DESCRIPTION = """
# Frame API Documentation

## Getting Started

To get started, you need to request credentials from us at [api-support@arch.co](mailto:api-support@arch.co).

We'll send you a secret link with the following information:

- a Client ID  
- a Client Secret  

---

### Authentication

To authenticate, you'll need to make a `POST` request to the `/client-api/v0/auth/token` endpoint.
Include your Client ID and Client Secret in the request body.


`
CLIENT_ID='<your client id>'
CLIENT_SECRET='<your client secret>'
curl \
  -X 'POST' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "clientId": "'"$CLIENT_ID"'",
    "clientSecret": "'"$CLIENT_SECRET"'"
  }' \
  'https://arch.co/client-api/v0/auth/token'`

---

### Querying

Once you have an access token, you can query the API as described below.  
The `authorization` header should include your Access Token, prefixed by the word `"Bearer"`  
(for example: `authorization: Bearer tokendata...`).

Here's an example with curl:

ACCESS_TOKEN='<access token from the previous step>'

curl -X 'GET' \
  'https://arch.co/client-api/v0/holdings' \
  -H 'accept: application/json' \
  -H "authorization: Bearer $ACCESS_TOKEN"---

### Rate Limit

The Arch Client API is **rate limited**, measured in requests per minute.  
If you hit this limit, you will get an **HTTP 429 - Too Many Requests** error.  
To address this, consider spacing out your requests.

To check your API user's rate limit status, view the response headers on an API request.  
The headers are as follows:

- **RateLimit-Policy**  
  The max number of requests allowed over a specified window of time.  
  Format: `[number of requests];w=[window of time in seconds]`.

- **RateLimit-Limit**  
  The max number of requests allowed over the current window of time.  
  Format: `[number of requests]`.

- **RateLimit-Remaining**  
  The remaining number of requests that the user is allowed to make over the current window of time.  
  Format: `[number of requests]`.

- **RateLimit-Reset**  
  The number of seconds remaining until the window of time resets.  
  Format: `[number of seconds]`.

---

## Pages

Many Arch objects can be returned in lists called **Pages**.  
By default, a Page contains up to **25 objects**.  
Some endpoints allow the user to increase the number of requested objects up to **1000**.

---

## Concepts

### Users

An individual's personal access to Arch.

### Accounts

Represents a collection of investments, which users are assigned to.

### Holdings

Holdings are investments, or any other piece of property (real estate, real assets, bank accounts, etc.).  
Each holding represents a relationship between an **Investing Entity** and an **Issuing Entity**,  
where the Investing Entity has invested in one of the **Offerings** that the Issuing Entity offers.

- #### Edge Cases

  Sometimes, a holding may not directly represent one of your investments.  
  For example, there might be a holding that contains tax documents related to a charitable contribution.  
  Holdings aren't always direct investments as well; it's not uncommon to see a holding representing a Fund → Fund investment.

### Investing Entities

These are the entities that **own holdings**.  
Arch receives and processes investments on behalf of the Investing Entity.

### Issuing Entities

These are the entities that **issue holdings**, which you are investing in.  
They issue documents and updates that Arch receives and processes.  
Typically, an issuing entity is a **PE fund**, **Hedge Fund**, etc.  
We also consider banks to be issuing entities who issue bank account holdings.

- #### Insights

  Insights are third-party data about issuing entities powered by our partner [Preqin](https://www.preqin.com).  
  Insights are accessible through the corresponding issuing entity.

### Offerings

These represent the different **investing opportunities** that an Issuing Entity offers.  
For example, Uber might offer both a Seed round and a later Series A round of investments.  
That would be a **single issuing entity** (Uber), with **two separate offerings** (Seed, Series A).

---

### Activities

Arch processes many types of documents and updates to your investments.  
Collectively, these updates are known as an **Activity**. Examples of activities include:

- Account Statement Received
- Capital Call Requested/Paid
- Distribution Notice/Paid
- Investor Letter

We process these activities and extract various **financial facts** about your activities.  
Examples of these financial facts are:

- Total Value (Capital Account)
- Total Contribution
- Total Distribution

### Cash Flows

These represent **money flowing into or out of your investments**, e.g. capital calls or distributions.  
One cash flow can be related to one or more activities and one or more **allocations**.

Each cash flow is linked to one or more allocations, which represent the specific movement of money.  
An allocation has a specific type and describes an event initiated by the LP or GP.  
Each allocation has a direction:

- `-1` → cash flowing **into** the investment  
- `1` → cash flowing **out of** the investment  
- `0` → no cash movement (infrequent)

The sum of the products of each allocation times its direction equals the **total cash flow** between the LP and the investment.  
These allocations can impact an investment's total value, contribution, remaining commitment, and distribution.

Types of allocations include:

- Capital Calls
- Expenses
- Cash Distributions
- Expenses

#### Point in Time Valuation vs. Estimated Value

**Point in time valuation** and **estimated value** report the value of an investment at different times.

- Point in time valuation returns the value of an investment exactly as reported on the most recent statement.
- Estimated value starts with the most recent statement value and adjusts according to the capital calls that have occurred since the date of the most recent statement.

### Tasks

A specific investment-related action that the user must complete.  
For example, confirming a new investment or verifying wire instructions.

---

### Lookthroughs

**Premium Feature:** Arch can track and display the  
<u title="An SOI returns a list of your investments, including metrics such as number of shares, fair value, and liquidity.">schedule of investments (SOI)</u> for any holdings you own.  
This allows you to **look through** the holdings you own to the investments that your holding made.  
This can make it easier to track your **true exposure**.

### Account User Roles

You grant access to accounts with **user roles**, which grant a set of permissions based on the role or "access type".  
The following set of roles is assignable through the API:

- Full Access
- Tax Only Access
- View Only (Full Access)
- File Only Access
- Informed Tax Only Access
- View Only with Task Completion Access
- Restricted Investor Access
- Investment Team Access

For a list of permissions associated with each role, please refer to  
[Arch Permissions by User Type](https://intercom.help/archhelp/en/articles/8975969-arch-permissions-by-user-type).

---

## Standards

### Time Zone

Dates and times are in **UTC** unless otherwise specified.
"""


API_DESCRIPTION_2 = r"""
<div class="renderedMarkdown"><h1>Frame API Documentation</h1>
<br/>
<h2>Getting Started</h2>
<p>Authentication and standard conventions for the Frame API.</p>

<table>
<tbody><tr>
<td>
<h3>Authentication</h3>
<p>To authenticate, you'll need to make a POST request to your authentication endpoint. Include your <b>Client ID</b> and <b>Client Secret</b> in the request body.</p>
<p>Using <a rel="noopener noreferrer" target="_blank" href="https://curl.se/">curl</a>, that request might look like this:</p>
<p><strong>Note:</strong> Tokens should be stored and reused until they expire.</p>
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
  'https://api.frame-platform.local/v1/auth/token'
</code></pre>
</td>
</tr>
</tbody></table>

<h2>Core APIs</h2>
<table>
<tbody><tr>
<td>
<h3>File Manager</h3>
<p>Manage your document lifecycle. Upload files, track their status (To Review, Approved, Completed), and retrieve detailed metadata or extraction results for specific documents using their Unique ID.</p>
<h3>Extraction & Business Rules</h3>
<p>Frame extracts data from documents and validates it against your custom business rules. You can manage these rules via the API and retrieve extraction configurations for specific document types.</p>
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
</tr></tbody></table></div>"""