"""Module client pour interagir avec l'API SAUR."""

# pylint: disable=E0401

import json
import logging
from typing import Any, Dict, Optional

import aiohttp

_LOGGER = logging.getLogger(__name__)

BASE_SAUR = "https://apib2c.azure.saurclient.fr"
BASE_DEV = "http://localhost:8080"
DEV = 1  # Définir la constante DEV ici
BASE_URL = BASE_SAUR if DEV == 0 else BASE_DEV


class SaurApiError(Exception):
    """Exception personnalisée pour les erreurs de l'API SAUR."""


class SaurClient:
    """Client pour interagir avec l'API SAUR."""

    TOKEN_URL = BASE_URL + "/admin/v2/auth"
    WEEKLY_URL = (
        BASE_URL
        + "/deli/section_subscription/{default_section_id}/"
        + "consumptions/weekly?year={year}&month={month}&day={day}"
    )
    MONTHLY_URL = (
        BASE_URL
        + "/deli/section_subscription/{default_section_id}/"
        + "consumptions/monthly?year={year}&month={month}"
    )
    LAST_URL = (
        BASE_URL
        + "/deli/section_subscriptions/{default_section_id}"
        + "/meter_indexes/last"
    )
    DELIVERY_URL = (
        BASE_URL
        + "/deli/section_subscriptions/{default_section_id}/"
        + "delivery_points"
    )
    USER_AGENT = (
        "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36"
        + " (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
    )

    def __init__(self, login: str, password: str) -> None:
        """Initialise le client SAUR.

        Args:
            login: L'identifiant pour l'API SAUR.
            password: Le mot de passe pour l'API SAUR.
        """
        self.login = login
        self.password = password
        self.access_token: Optional[str] = None
        self.default_section_id: Optional[str] = None
        self.headers: Dict[str, str] = {
            "User-Agent": self.USER_AGENT,
            "Content-Type": "application/json",
        }

    async def _async_request(
        self, method: str, url: str, payload: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Fonction générique pour les requêtes HTTP.

        Args:
            method: La méthode HTTP à utiliser (GET, POST, etc.).
            url: L'URL de l'API à interroger.
            payload: Les données à envoyer dans le corps de la "
                + "requête (pour les méthodes comme POST).

        Returns:
            Les données JSON de la réponse si la requête est réussie,
            sinon None.

        Raises:
            SaurApiError: En cas d'erreur lors de la requête API.
        """
        headers = self.headers.copy()  # Éviter de modifier l'original
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        _LOGGER.debug(
            "Request %s to %s, payload: %s, headers: %s", method, url, payload, headers
        )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method, url, json=payload, headers=headers
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    _LOGGER.debug(f"Response from {url}: {data}")
                    return data
        except aiohttp.ClientError as err:
            raise SaurApiError(f"Erreur API SAUR ({url}): {err}") from err
        except json.JSONDecodeError as err:
            raise SaurApiError(f"Erreur décodage JSON ({url}): {err}") from err

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
            method="POST", url=self.TOKEN_URL, payload=payload
        )
        if data:
            self.access_token = data.get("token", {}).get("access_token")
            self.default_section_id = data.get("defaultSectionId")
            _LOGGER.info("Authentification réussie.")

    async def get_weekly_data(
        self, year: int, month: int, day: int
    ) -> Optional[Dict[str, Any]]:
        """Récupère les données hebdomadaires.

        Args:
            year: L'année pour laquelle récupérer les données.
            month: Le mois pour lequel récupérer les données.
            day: Le jour pour lequel récupérer les données.

        Returns:
            Les données hebdomadaires si la requête est réussie,
            sinon None.
        """
        url = self.WEEKLY_URL.format(
            default_section_id=self.default_section_id,
            year=year, month=month, day=day
        )
        return await self._async_request(method="GET", url=url)

    async def get_monthly_data(
        self, year: int, month: int
    ) -> Optional[Dict[str, Any]]:
        """Récupère les données mensuelles.

        Args:
            year: L'année pour laquelle récupérer les données.
            month: Le mois pour lequel récupérer les données.

        Returns:
            Les données mensuelles si la requête est réussie, sinon None.
        """
        url = self.MONTHLY_URL.format(
            default_section_id=self.default_section_id, year=year, month=month
        )
        return await self._async_request(method="GET", url=url)

    async def get_lastknown_data(self) -> Optional[Dict[str, Any]]:
        """Récupère les dernières données connues.

        Returns:
            Les dernières données connues si la requête est réussie,
            sinon None.
        """
        url = self.LAST_URL.format(default_section_id=self.default_section_id)
        return await self._async_request(method="GET", url=url)

    async def get_deliverypoints_data(self) -> Optional[Dict[str, Any]]:
        """Récupère les points de livraison.

        Returns:
            Les points de livraison si la requête est réussie, sinon None.
        """
        url = self.DELIVERY_URL.format(
            default_section_id=self.default_section_id
        )
        return await self._async_request(method="GET", url=url)
