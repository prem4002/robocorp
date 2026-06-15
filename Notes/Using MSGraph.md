My robot

![[Pasted image 20260615105043.png]]
```
{
  "msgraph-credentials": {
    "tenant_id":     "xx",
    "client_id":     "yy",
    "client_secret": "secret~value"
  }
}
```

in [azure portal](portal.azure.com) we add the robot under azure active directory -> app registrations -> new registration
After creating a `new registration` we'll get the tenant and client id's which will be used in the `msgraph-credentials` 
for the secret, Certificated and secrets -> new secret 

After setting up, the msal (microsoft authentication libaray) is used to talk with azure, it helps me get an `access token` which is used to talk with the applications in msgraphs

```python
class GraphClient:
    """Authenticated Microsoft Graph client for RPA robots."""

    BASE_URL = "https://graph.microsoft.com/v1.0"
    
    def __init__(self):
        creds = vault.get_secret("msgraph-credentials")

        # this handles tokens and refresh (need to look into this more about how it works in the the backend)
        self._app = msal.ConfidentialClientApplication(
            client_id=creds["client_id"],
            client_credential=creds["client_secret"], #client-secret
            authority=f"https://login.microsoftonline.com/{creds['tenant_id']}",
        )
        self._session = requests.Session() #to reuse the same TCP session
        self._token   = None
        
    def _get_token(self) -> str:
    result = self._app.acquire_token_silent(
        scopes=["https://graph.microsoft.com/.default"],
        account=None
    )
    
    def _get_token(self) -> str:
        #trying cache first — the token might the present already, msal handles expiry automatically
        result = self._app.acquire_token_silent(
            scopes=["https://graph.microsoft.com/.default"],
            account=None
        )
        if not result:
            # Cache miss — fetch new token from Azure AD
            result = self._app.acquire_token_for_client(
                scopes=["https://graph.microsoft.com/.default"]
            )
        if "error" in result:
            raise RuntimeError(f"Token error: {result['error_description']}")
        return result["access_token"]
```

the `msgraph-credentials` is stored as a dictionary which contains three keys
	tenant_id — for the company (doesn't change)
	client_id — changes for each robot
	client_secret — api key

#### For fetching the tokens
---
**acquire_token_silent** — checks `msal` internal token cache first. If there's already a valid token that hasn't expired, it returns it immediately without making any network call.
**scopes=[".default"]** — tells `msal` what permissions you're requesting. The special `.default` scope means "give me all the Application permissions I've been granted in Azure Portal". You don't list individual permissions here — they're set in the Azure Portal app registration, not in code. `.default` picks them all up automatically.
**account=None** — in Client Credentials flow (app acting as itself), there's no user account involved. Pass `None` here. If you were using Delegated flow (app acting as a specific signed-in user), you'd pass the user's account object here.

When the token is already present the above happens, to get the token for the first time
`acquire_token_for_client` is used
