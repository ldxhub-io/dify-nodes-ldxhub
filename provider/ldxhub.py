from typing import Any

import requests

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class LdxhubProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            api_key = credentials.get("api_key")
            if not api_key:
                raise ValueError("API key is required.")

            base_url = credentials.get("base_url", "https://gw.ldxhub.io").rstrip("/")

            response = requests.get(
                f"{base_url}/refineloop/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10,
            )

            if response.status_code == 401 or response.status_code == 403:
                raise ValueError("Invalid API key.")

            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            raise ToolProviderCredentialValidationError(f"Failed to validate API key: {e}")
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))