"""Module client pour interagir avec l'API SAUR."""

# pylint: disable=E0401

import json
import logging
from typing import Any, Dict, Optional

import aiohttp

_LOGGER = logging.getLogger(__name__)

BASE_SAUR = "https://apib2c.azure.saurclient.fr"
BASE_DEV = "http://localhost:8080"
USER_AGENT = (
    "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36"
    + " (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
)

class SaurApiError(Exception):
    """Exception personnalisée pour les erreurs de l'API SAUR."""

class SaurClient:
    """Client pour interagir avec l'API SAUR."""

    token_url: str
    weekly_url: str
    monthly_url: str
    last_url: str
    delivery_url: str

    def __init__(self, login: str, password: str, dev_mode: bool = False) -> None:
        """Initialise le client SAUR.

        Args:
            login: L'identifiant pour l'API SAUR.
            password: Le mot de passe pour l'API SAUR.
            dev_mode: Indique si l'on utilise l'environnement de 
                      développement (True) ou non (False).
                      Par défaut, la valeur est False (environnement de production).
        """
        self.login = login
        self.password = password
        self.access_token: Optional[str] = None
        self.default_section_id: Optional[str] = None
        self.dev_mode = dev_mode
        self.base_url = BASE_SAUR if not self.dev_mode else BASE_DEV
        self.headers: Dict[str, str] = {
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
        }
        self.token_url = self.base_url + "/admin/v2/auth"
        self.weekly_url = (
            self.base_url
            + "/deli/section_subscription/{default_section_id}/"
            + "consumptions/weekly?year={year}&month={month}&day={day}"
        )
        self.monthly_url = (
            self.base_url
            + "/deli/section_subscription/{default_section_id}/"
            + "consumptions/monthly?year={year}&month={month}"
        )
        self.last_url = (
            self.base_url
            + "/deli/section_subscriptions/{default_section_id}"
            + "/meter_indexes/last"
        )
        self.delivery_url = (
            self.base_url
            + "/deli/section_subscriptions/{default_section_id}/"
            + "delivery_points"
        )

    async def _async_request(
        self, method: str, url: str, payload: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Fonction générique pour les requêtes HTTP avec gestion de la ré-authentification.

        Args:
            method: La méthode HTTP à utiliser (GET, POST, etc.).
            url: L'URL de l'API à interroger.
            payload: Les données à envoyer dans le corps de la
                     requête (pour les méthodes comme POST).

        Returns:
            Les données JSON de la réponse si la requête est réussie, sinon None.

        Raises:
            SaurApiError: En cas d'erreur lors de la requête API,
                          y compris après tentative de ré-authentification.
        """
        headers = self.headers.copy()
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        _LOGGER.debug(
            "Request %s to %s, payload: %s, headers: %s", method, url, payload, headers
        )

        for attempt in range(2):  # Tente la requête jusqu'à 2 fois (1 initiale + 1 après reauth)
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method, url, json=payload, headers=headers
                    ) as response:
                        response.raise_for_status()
                        data = await response.json()
                        _LOGGER.debug(f"Response from {url}: {data}")
                        return data
            except aiohttp.ClientResponseError as err:
                if err.status == 401 and attempt == 0:
                    _LOGGER.warning("Réponse 401, tentative de ré-authentification.")
                    await self.authenticate()
                    # Mise à jour du token dans les headers pour la prochaine tentative
                    headers["Authorization"] = f"Bearer {self.access_token}"
                else:
                    raise SaurApiError(f"Erreur API SAUR ({url}): {err}") from err
            except aiohttp.ClientError as err:
                raise SaurApiError(f"Erreur API SAUR ({url}): {err}") from err
            except json.JSONDecodeError as err:
                raise SaurApiError(f"Erreur décodage JSON ({url}): {err}") from err

        # Si on arrive ici après 2 tentatives et une erreur 401, on lève une exception
        raise SaurApiError("Échec de la requête après 2 tentatives "
                          + "(incluant la ré-authentification).")

    async def authenticate(self) -> None:
        """Authentifie le client et récupère les informations."""
        payload = {
            "username": self.login,
            "password": self.password,
            "client_id": "frontjs-client",
            "grant_type": "password",
            "scope": "api-scope",
            "isRecaptchaV3": True,
            "captchaToken": True,
        }
        data = await self._async_request(
            method="POST", url=self.token_url, payload=payload
        )
        if data:
            self.access_token = data.get("token", {}).get("access_token")
            self.default_section_id = data.get("defaultSectionId")
            _LOGGER.info("Authentification réussie.")
        else:
            raise SaurApiError("L'authentification a échoué.")

    async def get_weekly_data(
        self, year: int, month: int, day: int
    ) -> Optional[Dict[str, Any]]:
        """Récupère les données hebdomadaires."""
        url = self.weekly_url.format(
            default_section_id=self.default_section_id,
            year=year, month=month, day=day
        )
        return await self._async_request(method="GET", url=url)

    async def get_monthly_data(
        self, year: int, month: int
    ) -> Optional[Dict[str, Any]]:
        """Récupère les données mensuelles."""
        url = self.monthly_url.format(
            default_section_id=self.default_section_id, year=year, month=month
        )
        return await self._async_request(method="GET", url=url)

    async def get_lastknown_data(
      self
    ) -> Optional[Dict[str, Any]]:
        """Récupère les dernières données connues."""
        url = self.last_url.format(default_section_id=self.default_section_id)
        return await self._async_request(method="GET", url=url)

    async def get_deliverypoints_data(
      self
    ) -> Optional[Dict[str, Any]]:
        """Récupère les points de livraison."""
        url = self.delivery_url.format(
            default_section_id=self.default_section_id
        )
        return await self._async_request(method="GET", url=url)
