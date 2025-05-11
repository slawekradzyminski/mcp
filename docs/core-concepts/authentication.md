# Authentication

Authentication can be used by servers that want to expose tools accessing protected resources.

`mcp.server.auth` implements an OAuth 2.0 server interface, which servers can use by
providing an implementation of the `OAuthServerProvider` protocol.

```python
from mcp.server.fastmcp import FastMCP
from mcp.server.auth import AuthSettings, RevocationOptions, ClientRegistrationOptions

mcp = FastMCP("My App",
        auth_provider=MyOAuthServerProvider(),
        auth=AuthSettings(
            issuer_url="https://myapp.com",
            revocation_options=RevocationOptions(
                enabled=True,
            ),
            client_registration_options=ClientRegistrationOptions(
                enabled=True,
                valid_scopes=["myscope", "myotherscope"],
                default_scopes=["myscope"],
            ),
            required_scopes=["myscope"],
        ),
)
```

See [OAuthServerProvider](https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/server/auth/provider.py) for more details. 