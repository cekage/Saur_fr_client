import json
import logging
import asyncio
from saur_client import SaurClient

# Configuration du logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

try:
    with open("credentials.json", "r") as f:
        credentials = json.load(f)
        login = credentials.get("login")
        password = credentials.get("mdp")
        token = credentials.get("token", "")
        unique_id = credentials.get("unique_id", "")

        if not login or not password:
            raise ValueError("Le fichier credentials.json doit contenir 'login' et 'mdp'.")

except FileNotFoundError:
    print("Le fichier credentials.json est introuvable.")
    print("Créez un fichier credentials.json avec la structure suivante :")
    print('{"login": "votre_login", "mdp": "votre_mot_de_passe"}')
    exit()
except (json.JSONDecodeError, ValueError) as e:
    print(f"Erreur lors de la lecture du fichier credentials.json : {e}")
    print('Le fichier doit avoir la structure suivante : {"login": "votre_login", "mdp": "votre_mot_de_passe"}')
    exit()

async def main():
    client = None
    try:
        client = SaurClient(login=login, password=password, token=token, unique_id=unique_id)

        # Mise à jour du token et unique_id dans le fichier credentials.json
        # (uniquement si vides)
        if not credentials["token"] or not credentials["unique_id"]:
            credentials["token"] = client.access_token
            credentials["unique_id"] = client.default_section_id
            with open("credentials.json", "w") as f:
                json.dump(credentials, f, indent=4)

        delivery_points = await client.get_deliverypoints_data()
        print(delivery_points)
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
    finally:
        if client:
            await client.close_session()

if __name__ == "__main__":
    asyncio.run(main())