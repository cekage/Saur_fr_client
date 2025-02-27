import asyncio
import json
import logging
import sys
from dataclasses import dataclass
from pprint import pprint

import aiofiles

from saur_client import SaurClient

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


@dataclass(frozen=True, slots=True)
class SectionSubscriptionData:
    clientReference: str
    contractName: str
    sectionSubscriptionId: str
    isContractTerminated: bool


def extract_subscription_data(
    json_data: dict,
) -> list[SectionSubscriptionData]:
    """
    Extrait les informations des abonnements de section
    (SectionSubscriptionData) à partir d'un JSON donné.

    Args:
        json_data (Dict): Le JSON contenant les données des clients,
            contrats, et abonnements.

    Returns:
        list[SectionSubscriptionData]: Une liste
        d'objets SectionSubscriptionData."""

    subscription_list: list[SectionSubscriptionData] = []

    for client in json_data.get("clients", []):
        client_reference = client.get("clientReference", "")
        contract_name = client.get("contractName", "")

        for account in client.get("customerAccounts", []):
            for subscription in account.get("sectionSubscriptions", []):
                subscription_data = SectionSubscriptionData(
                    clientReference=client_reference,
                    contractName=contract_name,
                    sectionSubscriptionId=subscription.get(
                        "sectionSubscriptionId", ""
                    ),
                    isContractTerminated=subscription.get(
                        "isContractTerminated", False
                    )
                    == "True",  # Conversion en booléen
                )
                subscription_list.append(subscription_data)

    return subscription_list


try:
    with open("credentials.json") as f:
        credentials = json.load(f)
        login = credentials.get("login")
        password = credentials.get("mdp")
        token = credentials.get("token", "")
        unique_id = credentials.get("unique_id", "")
        client_id = credentials.get("clientId", "")
        _LOGGER.debug(f"\ntoken in json : {token}\n")

        if not login or not password:
            raise ValueError(
                "Le fichier credentials.json doit contenir 'login' et 'mdp'."
            )

except FileNotFoundError:
    print("Le fichier credentials.json est introuvable.")
    print("Créez un fichier credentials.json avec la structure suivante :")
    print('{"login": "votre_login", "mdp": "votre_mot_de_passe"}')
    sys.exit()
except (json.JSONDecodeError, ValueError) as e:
    print(f"Erreur lors de la lecture du fichier credentials.json : {e}")
    print(
        'Le fichier doit avoir la structure suivante : {'
        '"login": "votre_login", "mdp": "votre_mot_de_passe"}'
    )
    sys.exit()


async def main():
    client = None
    try:
        client = SaurClient(
            login=login,
            password=password,
            token=token,
            unique_id=unique_id,
            dev_mode=True,
        )
        delivery_points = await client.get_deliverypoints_data()

        credentials["token"] = client.access_token
        credentials["unique_id"] = client.default_section_id
        credentials["clientId"] = client.clientId
        sectionid = client.default_section_id

        async with aiofiles.open("credentials.json", "w") as f:
            await f.write(json.dumps(credentials, indent=4))
        print("****************************")
        chaine_json = json.dumps(credentials, indent=4)
        pprint(chaine_json)
        pprint(delivery_points)
        print("****************************")
        delivery_points = await client.get_contracts()
        subscription_data = extract_subscription_data(delivery_points)
        print("****************************")
        pprint(subscription_data)
        print("****************************")
        delivery_points = await client.get_monthly_data(2025, 2)
        delivery_points = await client.get_monthly_data(2025, 2, sectionid)
        delivery_points = await client.get_weekly_data(2024, 9, 1)
        delivery_points = await client.get_weekly_data(2024, 9, 1, sectionid)
        delivery_points = await client.get_lastknown_data()
        delivery_points = await client.get_lastknown_data(sectionid)

    except Exception as e:
        print(f"Une erreur est survenue : {e}")
    finally:
        if client:
            await client.close_session()


if __name__ == "__main__":
    asyncio.run(main())
