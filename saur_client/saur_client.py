"""Module client pour interagir avec l'API SAUR."""

# pylint: disable=E0401

import json
import logging
from typing import Any, Dict, Optional

import aiohttp

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

BASE_SAUR = "https://apib2c.azure.saurclient.fr"
BASE_DEV = "http://localhost:8080"
USER_AGENT = (
    "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36"
    + " (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
)

SaurResponse = dict[str, Any] | None


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
        self,
        login: str,
        password: str,
        unique_id: str = "",
        dev_mode: bool = False,
        token: str = "",
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
        self.login: str = login
        self.password: str = password
        self.access_token: str | None = token
        self.default_section_id: str = unique_id
        self.dev_mode: bool = dev_mode
        self.base_url: str = BASE_SAUR if not self.dev_mode else BASE_DEV
        self.headers: dict[str, str] = {
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
            "Pragma": "no-cache",
            "Referer": "https://mon-espace.saurclient.fr/",
            "Origin": "https://mon-espace.saurclient.fr/",
        }
        self.token_url: str = self.base_url + "/admin/v2/auth"
        self.weekly_url: str = (
            self.base_url
            + "/deli/section_subscription/{default_section_id}/"
            + "consumptions/weekly?year={year}&month={month}&day={day}"
        )
        self.monthly_url: str = (
            self.base_url
            + "/deli/section_subscription/{default_section_id}/"
            + "consumptions/monthly?year={year}&month={month}"
        )
        self.last_url: str = (
            self.base_url
            + "/deli/section_subscriptions/{default_section_id}"
            + "/meter_indexes/last"
        )
        self.delivery_url: str = (
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
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

    async def _authenticate(self) -> None:
        """Authentifie le client et récupère les informations. Fonction interne."""

        headers: dict[str, str] = (
            self.headers.copy()
        )  # On utilise les headers de base, sans Authorization

        # Utilisation de _build_auth_payload pour construire le payload
        payload: dict[str, Any] = _build_auth_payload(
            self.login, self.password
        )

        _LOGGER.debug(
            "Authenticating to %s, payload: %s, headers: %s",
            self.token_url,
            payload,
            headers,
        )

        try:
            # Utilisation de _execute_http_request pour effectuer la requête
            data: dict[str, Any] = await _execute_http_request(
                self.session, "POST", self.token_url, headers, payload
            )

            # Appel à la fonction de traitement de la réponse
            _process_auth_response(self, data)

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
        payload: SaurResponse = None,
        max_retries: int = 3,
        backoff_factor: float = 2,
    ) -> SaurResponse:
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

        headers: dict[str, str] = self.headers.copy()
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        # Version sécurisée des headers pour le logging
        safe_headers: dict[str, str] = {k: str(v) for k, v in headers.items()}

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
                data: SaurResponse = await _execute_http_request(
                    self.session, method, url, headers, payload
                )
                return data

            except SaurApiError as err:
                # Tentative de ré-authentification
                if not await _retry_authentication(
                    self, err, attempt, max_retries, headers
                ):
                    # Si _retry_authentication retourne False (ou lève une
                    # exception), on propage l'erreur
                    raise

        raise SaurApiError(
            f"Échec de la requête après {max_retries + 1} tentatives (incluant la ré-authentification)."
        )

    async def get_weekly_data(
        self, year: int, month: int, day: int
    ) -> SaurResponse:
        """Récupère les données hebdomadaires."""
        url: str = self.weekly_url.format(
            default_section_id=self.default_section_id,
            year=year,
            month=month,
            day=day,
        )
        return await self._async_request(method="GET", url=url)

    async def get_monthly_data(self, year: int, month: int) -> SaurResponse:
        """Récupère les données mensuelles."""
        url: str = self.monthly_url.format(
            default_section_id=self.default_section_id, year=year, month=month
        )
        return await self._async_request(method="GET", url=url)

    async def get_lastknown_data(self) -> SaurResponse:
        """Récupère les dernières données connues."""
        url: str = self.last_url.format(
            default_section_id=self.default_section_id
        )
        return await self._async_request(method="GET", url=url)

    async def get_deliverypoints_data(self) -> SaurResponse:
        """Récupère les points de livraison."""
        # Authentification si default_section_id n'est pas défini
        if not self.default_section_id:
            await self._authenticate()

        url: str = self.delivery_url.format(
            default_section_id=self.default_section_id
        )
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


async def _execute_http_request(
    session: aiohttp.ClientSession,
    method: str,
    url: str,
    headers: dict[str, str],
    payload: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Exécute la requête HTTP et gère les erreurs HTTP."""
    try:
        async with session.request(
            method, url, json=payload, headers=headers
        ) as response:
            response.raise_for_status()
            data: dict[str, Any] = await response.json()
            _LOGGER.debug(f"Response from {url}: {data}")
            return data
    except aiohttp.ClientResponseError as err:
        message = f"Erreur API SAUR ({url}): status: {err.status}, message: {err.message}"
        raise SaurApiError(message) from err
    except aiohttp.ClientError as err:
        message = f"Erreur API SAUR ({url}): {str(err)}"
        raise SaurApiError(message) from err
    except json.JSONDecodeError as err:
        message = f"Erreur décodage JSON ({url}): {str(err)}"
        raise SaurApiError(message) from err


def _build_auth_payload(login: str, password: str) -> dict[str, Any]:
    """Construit le payload pour la requête d'authentification."""
    payload: dict[str, Any] = {
        "username": login,
        "password": password,
        "client_id": "frontjs-client",
        "grant_type": "password",
        "scope": "api-scope",
        "isRecaptchaV3": True,
        "captchaToken": False,
    }
    return payload


def _process_auth_response(self: "SaurClient", data: dict[str, Any]) -> None:
    """Traite la réponse d'authentification et met à jour l'état de l'objet SaurClient."""
    if (
        data
        and data.get("token", {}).get("access_token")
        and data.get("defaultSectionId")
    ):
        self.access_token = data.get("token", {}).get("access_token")
        self.default_section_id = str(data.get("defaultSectionId"))
        _LOGGER.debug(
            "Authentification réussie. Réponse: %s",
            json.dumps(data, indent=2),  # JSON formaté avec indentation
        )
    else:
        _LOGGER.error("Réponse d'authentification invalide : %s", data)
        raise SaurApiError("L'authentification a échoué : données invalides.")


async def _retry_authentication(
    self: "SaurClient",
    err: SaurApiError,
    attempt: int,
    max_retries: int,
    headers: dict[str, str],
) -> bool:
    """Gère la ré-authentification en cas d'erreur 401 ou 403.

    Args:
        self: L'instance de SaurClient.
        err: L'exception SaurApiError à gérer.
        attempt: Le numéro de la tentative actuelle.
        max_retries: Le nombre maximum de tentatives.
        headers: Les headers de la requête (pour mise à jour du token).

    Returns:
        True si la ré-authentification a réussi et la requête peut être retentée, False sinon.

    Raises:
        SaurApiError: Si le nombre maximum de tentatives est atteint
        ou si l'erreur n'est pas une erreur 401 ou 403.
    """
    if "status: 401" in str(err) or "status: 403" in str(err):
        if attempt < max_retries:
            _LOGGER.warning(
                "Réponse %s, tentative de ré-authentification (tentative %s/%s).",
                err,
                attempt + 1,
                max_retries,
            )
            # On réinitialise le token pour forcer une nouvelle authentification
            self.access_token = None
            await self._authenticate()
            headers["Authorization"] = f"Bearer {self.access_token}"

            return True  # Indique que la requête peut être retentée
        else:
            _LOGGER.error(
                "Réponse %s, nombre maximum de tentatives de ré-authentification atteint.",
                err,
            )
            raise SaurApiError(
                f"Nombre maximum de tentatives de ré-authentification atteint: {err}"
            ) from err
    else:
        raise err  # On relève l'erreur si ce n'est pas une erreur 401/403
