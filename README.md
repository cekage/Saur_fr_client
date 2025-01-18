# saur_client

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=cekage_Saur_fr_client&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=cekage_Saur_fr_client)
[![PyPI version](https://badge.fury.io/py/saur_client.svg)](https://badge.fury.io/py/saur_client)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Français

**Client Python pour interagir avec l'API SAUR**

Ce package fournit une interface simple et asynchrone pour interagir avec l'API du fournisseur d'eau SAUR. Il permet de récupérer des données de consommation hebdomadaires, mensuelles, les dernières données connues du compteur et les points de livraison.

### Installation

Vous pouvez installer `saur_client` depuis PyPI en utilisant pip :

```bash
pip install saur_client
```

### Utilisation

Voici un exemple basique d'utilisation de la librairie :

```python
import asyncio
from saur_client.saur_client import SaurClient

async def main():
    """Exemple d'utilisation de la librairie saur_client."""
    client = SaurClient(login="votre_login", password="votre_mot_de_passe")

    try:
        await client.authenticate()
        print("Authentification réussie !")

        # Récupérer les données hebdomadaires
        weekly_data = await client.get_weekly_data(year=2024, month=5, day=15)
        print("Données hebdomadaires:", weekly_data)

        # Récupérer les données mensuelles
        monthly_data = await client.get_monthly_data(year=2024, month=5)
        print("Données mensuelles:", monthly_data)

        # Récupérer les dernières données connues
        last_data = await client.get_lastknown_data()
        print("Dernières données connues:", last_data)

        # Récupérer les points de livraison
        delivery_points = await client.get_deliverypoints_data()
        print("Points de livraison:", delivery_points)

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Explication :**

1. **Importation :** Importez la classe `SaurClient` depuis le package `saur_client`.
2. **Instanciation :** Créez une instance de `SaurClient` en fournissant votre `login` et `password` SAUR.
3. **Authentification :** Appelez la méthode `authenticate()` pour obtenir un token d'accès.
4. **Récupération des données :** Utilisez les méthodes `get_weekly_data()`, `get_monthly_data()`, `get_lastknown_data()`, et `get_deliverypoints_data()` pour récupérer les informations souhaitées.
5. **Gestion des erreurs :** Enveloppez votre code dans un bloc `try...except` pour gérer les éventuelles exceptions.

### Documentation

[Lien vers la documentation complète (si vous en avez une, par exemple sur Read the Docs)]

### Contribution

Les contributions sont les bienvenues ! Si vous souhaitez améliorer `saur_client`, n'hésitez pas à soumettre des pull requests ou à signaler des issues sur le dépôt GitHub.

### Licence

Ce projet est sous licence [MIT License](LICENSE) - consultez le fichier [LICENSE](LICENSE) pour plus de détails.

### Remerciements

Wife and kids, for everything ! 

---

## English

**Python client to interact with the SAUR API**

This package provides a simple and asynchronous interface for interacting with the API of the SAUR water provider. It allows you to retrieve weekly and monthly consumption data, the latest known meter readings, and delivery points.

### Installation

You can install `saur_client` from PyPI using pip:

```bash
pip install saur_client
```

### Usage

Here's a basic example of how to use the library:

```python
import asyncio
from saur_client.saur_client import SaurClient

async def main():
    """Example of using the saur_client library."""
    client = SaurClient(login="your_login", password="your_password")

    try:
        await client.authenticate()
        print("Authentication successful!")

        # Retrieve weekly data
        weekly_data = await client.get_weekly_data(year=2024, month=5, day=15)
        print("Weekly data:", weekly_data)

        # Retrieve monthly data
        monthly_data = await client.get_monthly_data(year=2024, month=5)
        print("Monthly data:", monthly_data)

        # Retrieve the latest known data
        last_data = await client.get_lastknown_data()
        print("Latest known data:", last_data)

        # Retrieve delivery points
        delivery_points = await client.get_deliverypoints_data()
        print("Delivery points:", delivery_points)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Explanation:**

1. **Importing:** Import the `SaurClient` class from the `saur_client` package.
2. **Instantiation:** Create an instance of `SaurClient` by providing your SAUR `login` and `password`.
3. **Authentication:** Call the `authenticate()` method to obtain an access token.
4. **Data Retrieval:** Use the `get_weekly_data()`, `get_monthly_data()`, `get_lastknown_data()`, and `get_deliverypoints_data()` methods to retrieve the desired information.
5. **Error Handling:** Wrap your code in a `try...except` block to handle potential exceptions.

### Documentation

[Link to the complete documentation (if you have one, for example on Read the Docs)]

### Contributing

Contributions are welcome! If you'd like to improve `saur_client`, feel free to submit pull requests or report issues on the GitHub repository.

### License

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.

### Acknowledgements

Wife and kids, for everything ! 
