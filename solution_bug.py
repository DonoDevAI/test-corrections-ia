"""
Fix pour le bug dans l'outil `chercher_bugs_open_source`.

PROBLEME IDENTIFIE :
L'outil echoue avec l'erreur "Query must include 'is:issue' or 'is:pull-request'"
car la fonction de construction de requete ne rajoute pas le qualificateur
requis par l'API GitHub Search.

BUGS SUPPLEMENTAIRES CORRIGES :
1. Doublon du parametre per_page : per_page etait ajoute dans la query string
   par build_query ET dans le dictionnaire params de la requete HTTP.
2. Gestion de la query vide : un espace en trop pouvait apparaitre au debut
   de la requete si query etait vide ou si le qualificatif etait deja present.
3. build_query ne doit construire que la partie 'q' de la requete,
   pas les parametres de pagination.

SOLUTION :
- Retirer per_page de la construction de la query dans build_query.
- Gerer correctement les cas ou query est vide.
- Laisser per_page uniquement dans les params de la requete HTTP.
"""


def build_query(langage: str, limite: int, query: str, type_recherche: str = "issue") -> str:
    """
    Construit une requete valide pour l'API GitHub Search.

    L'API GitHub exige que la requete de recherche contienne obligatoirement
    le qualificateur 'is:issue' ou 'is:pull-request' pour filtrer le type
    de resultat recherche.

    Args:
        langage: Le langage de programmation cible (ex: "python").
        limite: Le nombre maximum de resultats a retourner.
        query: La requete de recherche fournie par l'utilisateur.
        type_recherche: Le type de resultat ("issue" ou "pull-request").
                        Par defaut a "issue".

    Returns:
        Une chaine de requete valide conforme a l'API GitHub Search.

    Raises:
        ValueError: Si type_recherche n'est ni "issue" ni "pull-request".
    """
    # Validation du type de recherche
    if type_recherche not in ("issue", "pull-request"):
        raise ValueError(
            "type_recherche doit etre 'issue' ou 'pull-request'. "
            "L'API GitHub exige un qualificateur de type valide."
        )

    # Nettoyage de la query fournie : retirer les espaces superflus
    query_clean = query.strip()

    # Verifier si le qualificateur 'is:issue' ou 'is:pull-request' est deja present
    # dans la requete pour eviter les doublons
    qualificateur = f"is:{type_recherche}"
    if qualificateur not in query_clean:
        # Ajouter le qualificateur requis par l'API GitHub
        # C'est la CORRECTION principale du bug
        if query_clean:
            query_clean = f"{query_clean} {qualificateur}"
        else:
            query_clean = qualificateur

    # Ajouter le filtre par langage si specifie
    if langage:
        query_clean = f"{query_clean} language:{langage}"

    # CORRECTION : on ne concatene plus per_page ici.
    # per_page est gere uniquement dans les parametres de la requete HTTP
    # pour eviter le doublon avec le dictionnaire params.

    return query_clean


def chercher_bugs_open_source(langage: str, limite: int, query: str, type_recherche: str = "issue") -> dict:
    """
    Fonction corrigee de recherche de bugs open source sur GitHub.

    Cette fonction corrige le bug original en s'assurant que la requete
    construite contient toujours le qualificateur 'is:issue' ou 'is:pull-request'
    requis par l'API GitHub Search API.

    Args:
        langage: Le langage de programmation (ex: "python").
        limite: Nombre max de resultats.
        query: Termes de recherche.
        type_recherche: Type de resultat ("issue" ou "pull-request").

    Returns:
        Dictionnaire contenant les resultats de la recherche.
    """
    import requests  # Import effectue ici pour garder l'exemple autonome

    # Construire la requete VALIDE grace a la fonction corrigee
    requete = build_query(langage, limite, query, type_recherche)

    # URL de l'API GitHub Search
    url = "https://api.github.com/search/issues"

    # Headers d'authentification (optionnel mais recommande)
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "chercher_bugs_open_source/1.0"
    }

    # Parametres de la requete
    # CORRECTION : per_page est uniquement ici, plus dans build_query
    params = {
        "q": requete,
        "per_page": limite
    }

    # Execution de la requete API
    response = requests.get(url, params=params, headers=headers)

    # Verification de la response
    if response.status_code == 200:
        return response.json()
    else:
        raise RuntimeError(
            f"Erreur lors de la requete GitHub API: "
            f"Code {response.status_code} - {response.text}"
        )


# === EXEMPLES D'UTILISATION ===

if __name__ == "__main__":
    # Avant le fix : la requete aurait ete invalide et aurait echoue
    # avec "Query must include 'is:issue' or 'is:pull-request'"

    # Exemple 1 : Recherche d'issues Python
    requete1 = build_query(langage="python", limite=10, query="bug authentication", type_recherche="issue")
    print(f"Requete 1 (issue): {requete1}")
    # Resultat attendu : "bug authentication is:issue language:python"

    # Exemple 2 : Recherche de pull-requests Python
    requete2 = build_query(langage="python", limite=5, query="security fix", type_recherche="pull-request")
    print(f"Requete 2 (pull-request): {requete2}")
    # Resultat attendu : "security fix is:pull-request language:python"

    # Exemple 3 : Query contient deja le qualificateur (pas de doublon)
    requete3 = build_query(langage="python", limite=10, query="bug is:issue", type_recherche="issue")
    print(f"Requete 3 (deja presente): {requete3}")
    # Resultat attendu : "bug is:issue language:python"
    # Le qualificateur n'est pas ajoute deux fois

    # Exemple 4 : Query vide
    requete4 = build_query(langage="python", limite=10, query="", type_recherche="issue")
    print(f"Requete 4 (vide): {requete4}")
    # Resultat attendu : "is:issue language:python"
