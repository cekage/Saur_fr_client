# saur_client

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=cekage_Saur_fr_client&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=cekage_Saur_fr_client)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![PyPI version](https://badge.fury.io/py/saur_client.svg)](https://badge.fury.io/py/saur_client)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)  <!-- Remplacez par votre licence -->

## Français - French

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
import json
from saur_client.saur_client import SaurClient

async def main():
    """Exemple d'utilisation de la librairie saur_client."""
    try:
        with open("credentials.json", "r") as f:
            credentials = json.load(f)
    except FileNotFoundError:
        print("Erreur : le fichier credentials.json est introuvable.")
        print("Créez un fichier credentials.json avec la structure suivante :")
        print('{"login": "votre_login", "mdp": "votre_mot_de_passe", "token": "votre_token", "unique_id": "votre_unique_id"}')
        print("Les champs 'token' et 'unique_id' sont optionnels.")
        return
    
    # Les valeurs "" pour token et unique_id forceront une authentification
    async with SaurClient(
        login=credentials.get("login"),
        password=credentials.get("mdp"),
        token=credentials.get("token", ""),
        unique_id=credentials.get("unique_id", "")
    ) as client:
        try:
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
2. **Instanciation :** Créez une instance de `SaurClient` en fournissant votre `login`, `password`, et optionnellement un `token` et `unique_id` SAUR.
    *   Si vous fournissez un `token` valide et un `unique_id`, l'authentification sera ignorée.
    *   Si `token` ou `unique_id` sont manquants ou invalides, le client s'authentifiera automatiquement.
3. **`async with` :** Utilisez `async with` pour gérer la session du client. La session sera automatiquement fermée à la fin du bloc.
4. **Récupération des données :** Utilisez les méthodes `get_weekly_data()`, `get_monthly_data()`, `get_lastknown_data()`, et `get_deliverypoints_data()` pour récupérer les informations souhaitées.
5. **Gestion des erreurs :** Enveloppez votre code dans un bloc `try...except` pour gérer les éventuelles exceptions.

**Gestion avancée des requêtes**

La méthode `_async_request` de `SaurClient` supporte les paramètres suivants :

*   `max_retries` (int) : Le nombre maximum de tentatives de ré-authentification en cas d'erreur 401 ou 403 (par défaut : 3).
*   `backoff_factor` (float) : Le facteur multiplicateur pour le délai entre chaque tentative (par défaut : 2).

Ces paramètres peuvent être modifiés lors d'un appel à une méthode `get_xxx_data` :

```python
# Exemple avec get_weekly_data
weekly_data = await client.get_weekly_data(year=2024, month=5, day=15, max_retries=5, backoff_factor=1.5)
```

**Implémentation de référence**

Le fichier [`simple_test.py`](./simple_test.py) dans le dépôt GitHub fournit une implémentation de référence simple pour l'utilisation de `saur_client`.

### Documentation

[Lien vers la documentation complète (si vous en avez une, par exemple sur Read the Docs)]

### Contribution

Les contributions sont les bienvenues ! Si vous souhaitez améliorer `saur_client`, n'hésitez pas à soumettre des pull requests ou à signaler des issues sur le dépôt GitHub.

### Licence

Ce projet est sous licence \[MIT License](LICENSE) - consultez le fichier [LICENSE](LICENSE) pour plus de détails.

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
import json
from saur_client.saur_client import SaurClient

async def main():
    """Example of using the saur_client library."""
    try:
        with open("credentials.json", "r") as f:
            credentials = json.load(f)
    except FileNotFoundError:
        print("Error: credentials.json file not found.")
        print("Create a credentials.json file with the following structure:")
        print('{"login": "your_login", "mdp": "your_password", "token": "your_token", "unique_id": "your_unique_id"}')
        print("The 'token' and 'unique_id' fields are optional.")
        return

    # Empty strings "" for token and unique_id will force authentication
    async with SaurClient(
        login=credentials.get("login"),
        password=credentials.get("mdp"),
        token=credentials.get("token", ""),
        unique_id=credentials.get("unique_id", "")
    ) as client:
        try:
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
2. **Instantiation:** Create an instance of `SaurClient` by providing your SAUR `login`, `password`, and optionally a `token` and `unique_id`.
    *   If you provide a valid `token` and `unique_id`, authentication will be skipped.
    *   If `token` or `unique_id` are missing or invalid, the client will authenticate automatically.
3. **`async with`:** Use `async with` to manage the client's session. The session will be automatically closed at the end of the block.
4. **Data Retrieval:** Use the `get_weekly_data()`, `get_monthly_data()`, `get_lastknown_data()`, and `get_deliverypoints_data()` methods to retrieve the desired information.
5. **Error Handling:** Wrap your code in a `try...except` block to handle potential exceptions.

**Advanced Request Management**

The `_async_request` method of `SaurClient` supports the following parameters:

*   `max_retries` (int): The maximum number of re-authentication attempts in case of a 401 or 403 error (default: 3).
*   `backoff_factor` (float): The multiplier for the delay between each attempt (default: 2).

These parameters can be modified when calling a `get_xxx_data` method:

```python
# Example with get_weekly_data
weekly_data = await client.get_weekly_data(year=2024, month=5, day=15, max_retries=5, backoff_factor=1.5)
```

**Reference Implementation**

The [`simple_test.py`](./simple_test.py) file in the GitHub repository provides a simple reference implementation for using `saur_client`.

### Documentation

[Link to the complete documentation (if you have one, for example on Read the Docs)]

### Contributing

Contributions are welcome! If you'd like to improve `saur_client`, feel free to submit pull requests or report issues on the GitHub repository.

### License

This project is licensed under the \[MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.

### Acknowledgements

Wife and kids, for everything !
```

J'ai simplifié l'exemple de code, ajouté des informations sur les paramètres `token` et `unique_id`, et précisé que `simple_test.py` est une implémentation de référence. J'ai également ajouté la section sur la gestion avancée des requêtes, expliquant `max_retries` et `backoff_factor`.

N'hésite pas à me faire part de tes commentaires ou suggestions d'amélioration !
