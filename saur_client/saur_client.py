"""Module client pour interagir avec l'API SAUR."""

# pylint: disable=E0401

import json
import logging
from typing import Any, Dict, Optional
import asyncio

import aiohttp

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

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

    def __init__(
        self, login: str, password: str, unique_id: str = "", dev_mode: bool = False,
        token: str = ""
    ) -> None:
        """Initialise le client SAUR.

        Args:
            login: L'identifiant pour l'API SAUR.
            password: Le mot de passe pour l'API SAUR.
            unique_id: L'identifiant unique du compteur.
            dev_mode: Indique si l'on utilise l'environnement de
                      développement (True) ou non (False).
                      Par défaut, la valeur est False (environnement de production).
            token: Le token pour économiser un auth().
        """
        self.login = login
        self.password = password
        self.access_token: str = token
        self.default_section_id: str = unique_id
        self.dev_mode = dev_mode
        self.base_url = BASE_SAUR if not self.dev_mode else BASE_DEV
        self.headers: Dict[str, str] = {
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
            "Pragma": "no-cache",
            "Referer": "https://mon-espace.saurclient.fr/",
            "Origin": "https://mon-espace.saurclient.fr/"
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
        _LOGGER.debug(
            "Login %s Password %s, unique_id %s, dev_mode %s",
            login,
            password,
            unique_id,
            dev_mode,
        )
        # Initialisation de la session dès le __init__
        self.session = aiohttp.ClientSession()

    async def _authenticate(self) -> None:
        """Authentifie le client et récupère les informations. Fonction interne."""
        payload = {
            "username": self.login,
            "password": self.password,
            "client_id": "frontjs-client",
            "grant_type": "password",
            "scope": "api-scope",
            "isRecaptchaV3": True,
            "captchaToken": False,
        }

        headers = self.headers.copy()  # On utilise les headers de base, sans Authorization

        _LOGGER.debug(
            "Authenticating to %s, payload: %s, headers: %s",
            self.token_url,
            payload,
            headers,
        )

        try:
            async with self.session.post(
                self.token_url, json=payload, headers=headers
            ) as response:
                response.raise_for_status()
                data = await response.json()

                if (
                    data
                    and data.get("token", {}).get("access_token")
                    and data.get("defaultSectionId")
                ):
                    self.access_token = data.get("token", {}).get("access_token")
                    self.default_section_id = data.get("defaultSectionId")
                    _LOGGER.info("Authentification réussie.")
                else:
                    _LOGGER.error("Réponse d'authentification invalide : %s", data)
                    raise SaurApiError(
                        "L'authentification a échoué : données invalides."
                    )

        except aiohttp.ClientResponseError as err:
            message = f"Erreur API SAUR lors de l'authentification ({self.token_url}): status: {err.status}, message: {err.message}"
            raise SaurApiError(message) from err
        except aiohttp.ClientError as err:
            message = f"Erreur API SAUR lors de l'authentification ({self.token_url}): {str(err)}"
            raise SaurApiError(message) from err
        except json.JSONDecodeError as err:
            message = f"Erreur décodage JSON lors de l'authentification ({self.token_url}): {str(err)}"
            raise SaurApiError(message) from err

    async def _async_request(
        self,
        method: str,
        url: str,
        payload: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        backoff_factor: float = 2,
    ) -> Optional[Dict[str, Any]]:
        """Fonction générique pour les requêtes HTTP avec gestion de la ré-authentification.

        Args:
            method: La méthode HTTP à utiliser (GET, POST, etc.).
            url: L'URL de l'API à interroger.
            payload: Les données à envoyer dans le corps de la
                     requête (pour les méthodes comme POST).
            max_retries: Le nombre maximum de tentatives de ré-authentification.
            backoff_factor: Le facteur d'augmentation du délai entre chaque tentative.

        Returns:
            Les données JSON de la réponse si la requête est réussie, sinon None.

        Raises:
            SaurApiError: En cas d'erreur lors de la requête API,
                          y compris après tentative de ré-authentification.
        """
        headers = self.headers.copy()
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        # Version sécurisée des headers pour le logging
        safe_headers = {k: str(v) for k, v in headers.items()}

        _LOGGER.debug(
            "Request %s to %s, payload: %s, headers: %s",
            method,
            url,
            payload,
            safe_headers,
        )

        for attempt in range(max_retries + 1):
            # On vérifie ici que le token et l'ID sont définis
            if not self.access_token or not self.default_section_id:
                await self._authenticate()
                headers["Authorization"] = f"Bearer {self.access_token}"

            try:
                async with self.session.request(
                    method, url, json=payload, headers=headers
                ) as response:
                    # Gestion des erreurs 401 et 403 uniquement
                    if response.status == 401 or response.status == 403:
                        if attempt < max_retries:
                            _LOGGER.warning(
                                "Réponse %s, tentative de ré-authentification (tentative %s/%s).",
                                response.status,
                                attempt + 1,
                                max_retries,
                            )
                            self.access_token = (
                                None
                            )  # On réinitialise le token pour forcer une nouvelle authentification
                            await self._authenticate()
                            headers["Authorization"] = f"Bearer {self.access_token}"

                            # Calcul du délai avant la prochaine tentative (backoff exponentiel)
                            delay = backoff_factor**attempt
                            _LOGGER.debug(
                                f"Attente de {delay:.2f} secondes avant la prochaine tentative."
                            )
                            await asyncio.sleep(delay)
                            continue
                        else:
                            _LOGGER.error(
                                "Réponse %s, nombre maximum de tentatives de ré-authentification atteint.",
                                response.status,
                            )

                    response.raise_for_status()
                    data = await response.json()
                    _LOGGER.debug(f"Response from {url}: {data}")
                    return data

            except aiohttp.ClientResponseError as err:
                message = (
                    f"Erreur API SAUR ({url}): status: {err.status}, message: {err.message}"
                )
                raise SaurApiError(message) from err
            except aiohttp.ClientError as err:
                message = f"Erreur API SAUR ({url}): {str(err)}"
                raise SaurApiError(message) from err
            except json.JSONDecodeError as err:
                message = f"Erreur décodage JSON ({url}): {str(err)}"
                raise SaurApiError(message) from err

        raise SaurApiError(
            f"Échec de la requête après {max_retries + 1} tentatives (incluant la ré-authentification)."
        )

    async def get_weekly_data(
        self, year: int, month: int, day: int
    ) -> Optional[Dict[str, Any]]:
        """Récupère les données hebdomadaires."""
        url = self.weekly_url.format(
            default_section_id=self.default_section_id, year=year, month=month, day=day
        )
        return await self._async_request(method="GET", url=url)

    async def get_monthly_data(self, year: int, month: int) -> Optional[Dict[str, Any]]:
        """Récupère les données mensuelles."""
        url = self.monthly_url.format(
            default_section_id=self.default_section_id, year=year, month=month
        )
        return await self._async_request(method="GET", url=url)

    async def get_lastknown_data(self) -> Optional[Dict[str, Any]]:
        """Récupère les dernières données connues."""
        url = self.last_url.format(default_section_id=self.default_section_id)
        return await self._async_request(method="GET", url=url)

    async def get_deliverypoints_data(self) -> Optional[Dict[str, Any]]:
        """Récupère les points de livraison."""
        url = self.delivery_url.format(default_section_id=self.default_section_id)
        return await self._async_request(method="GET", url=url)

    async def close_session(self) -> None:
        """Ferme la session aiohttp."""
        await self.__aexit__(None, None, None)

    async def __aenter__(self):
        """Initialise la session aiohttp si nécessaire."""
        # La session est déjà initialisée dans __init__
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Ferme la session aiohttp."""
        if self.session:
            await self.session.close()
            self.session = None