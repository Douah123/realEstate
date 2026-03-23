# Estimation immobiliere

Projet de prediction du prix d'un bien immobilier a partir de quelques caracteristiques principales.

Le projet s'appuie sur le dataset **Ames Housing**, un jeu de donnees sur les ventes de maisons realisees dans la ville de **Ames** entre **2006 et 2010**.

Le projet contient :

- une API Flask qui expose un endpoint de prediction ;
- un front HTML simple qui consomme cette API ;
- un notebook d'entrainement du modele ;
- un modele serialize avec `joblib` ;
- un modele SQLAlchemy pour enregistrer les predictions si la base est active.

Ce README couvre le projet et son fonctionnement.

## Objectif

L'application estime un prix immobilier a partir des donnees suivantes :

- qualite generale ;
- annee de construction ;
- surface habitable ;
- surface du 1er etage ;
- surface du 2eme etage ;
- surface totale du sous-sol ;
- surface du garage ;
- surface du terrain ;
- total des salles de bain ;
- presence de climatisation centrale.

L'API transforme ces donnees en variables compatibles avec le pipeline de machine learning, lance la prediction, puis renvoie un resultat JSON.

## Structure du projet

```text
projet_cloud_api/
|-- app.py
|-- config.py
|-- routes.py
|-- prediction_service.py
|-- models.py
|-- wsgi.py
|-- requirements.txt
|-- .env.example
|-- README.md
|-- DEPLOYMENT.md
|-- entrainement_modele.ipynb
|-- model_pipeline_complet4.pkl
`-- templates/
    |-- index.html
    |-- app-config.js
    `-- app-config.example.js
```

## Composants principaux

### API Flask

Le backend est assemble dans `app.py`.

Il s'appuie sur :

- `config.py` pour la configuration ;
- `routes.py` pour les routes API ;
- `prediction_service.py` pour le chargement du modele et la preparation des donnees ;
- `models.py` pour le modele de persistance.

### Front HTML

Le front principal est dans `templates/index.html`.

Il :

- affiche le formulaire ;
- construit le JSON a envoyer ;
- appelle `POST /predict` ;
- affiche la prediction retournee par l'API.

Le fichier `templates/app-config.js` permet de definir l'URL de l'API consommee par le front.

### Modele ML

Le pipeline sauvegarde dans `model_pipeline_complet4.pkl` est charge via `joblib`.

Il utilise une fonction de pretraitement `preprocess_ames`, conservee dans `prediction_service.py`, car le pickle en depend au chargement.

## Installation locale

### 1. Creer et activer un environnement virtuel

Sous Windows PowerShell :

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Sous Linux/macOS :

```bash
python -m venv venv
source venv/bin/activate
```

### 2. Installer les dependances

```bash
pip install -r requirements.txt
```

### 3. Creer le fichier d'environnement

Copie `.env.example` vers `.env`.

Exemple simple pour du local sans enregistrement en base :

```env
FLASK_ENV=development
FLASK_DEBUG=true
FLASK_HOST=0.0.0.0
PORT=8000
ENABLE_DB_RECORDING=false
AUTO_CREATE_DB=false
MODEL_PATH=model_pipeline_complet4.pkl
FRONTEND_ORIGINS=*
```

### 4. Lancer l'API

```bash
python app.py
```

L'API sera disponible sur :

```text
http://127.0.0.1:8000
```

## Utilisation de l'API

### Endpoint principal

`POST /predict`

Content-Type attendu :

```text
application/json
```

### Exemple de payload

```json
{
  "qualite_generale": 6,
  "surface_habitable": 1400,
  "surface_1er_etage": 900,
  "surface_2eme_etage": 500,
  "surface_totale_sous_sol": 900,
  "surface_garage": 350,
  "surface_terrain": 7000,
  "annee_construction": 2005,
  "total_salles_bain": 2.5,
  "climatisation_centrale": "y"
}
```

### Exemple avec curl

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "qualite_generale": 6,
    "surface_habitable": 1400,
    "surface_1er_etage": 900,
    "surface_2eme_etage": 500,
    "surface_totale_sous_sol": 900,
    "surface_garage": 350,
    "surface_terrain": 7000,
    "annee_construction": 2005,
    "total_salles_bain": 2.5,
    "climatisation_centrale": "y"
  }'
```

### Exemple de reponse

```json
{
  "ok": true,
  "prediction": 211236.41046638,
  "confidence_interval": {
    "level": 0.95,
    "lower_bound": 176420.0,
    "upper_bound": 243180.0
  },
  "prediction_text": "Prix predit : 211,236 $",
  "confidence_interval_text": "Intervalle de confiance 95% : [176,420 $, 243,180 $]",
  "prediction_id": null
}
```

`prediction_id` vaut `null` si l'enregistrement base de donnees est desactive.

## Front HTML

Le front peut etre ouvert comme page statique et appeler l'API.

Resolution de l'URL de l'API dans `templates/index.html` :

1. `window.APP_CONFIG.apiBaseUrl` si defini ;
2. `localStorage.api_base_url` si defini ;
3. `http://127.0.0.1:8000` en local ;
4. `window.location.origin` en dernier recours.

Exemple de fichier `templates/app-config.js` :

```js
window.APP_CONFIG = {
  apiBaseUrl: "http://127.0.0.1:8000"
};
```

## Enregistrement des predictions

Le modele `models.py` definit une table `predictions`.

Champs stockes :

- variables d'entree principales ;
- valeur predite ;
- date de creation.

L'enregistrement est controle par :

```env
ENABLE_DB_RECORDING=true
```

Si cette variable est a `false`, l'API continue a predire mais n'enregistre rien.

## Entrainement du modele

L'entrainement se trouve dans `entrainement_modele.ipynb`.

Cette partie est importante, car l'API depend directement du pipeline cree dans ce notebook.

Le modele a ete construit a partir du dataset **Ames Housing**, qui regroupe des informations sur des ventes de maisons effectuees dans la ville de **Ames** entre **2006 et 2010**.

### Ce que fait le notebook

Le notebook :

- charge et nettoie les donnees ;
- fait du feature engineering ;
- prepare les variables utiles au modele ;
- entraine un pipeline scikit-learn ;
- sauvegarde le pipeline avec `joblib`.

### Pipeline utilise

Le pipeline entraine suit cette logique :

1. pretraitement via `preprocess_ames` ;
2. normalisation avec `MinMaxScaler` ;
3. regression avec `RandomForestRegressor`.

Le modele final sauvegarde est ensuite exporte dans :

```text
model_pipeline_complet4.pkl
```

### Metriques de performance

Lors de l'evaluation dans le notebook, le modele obtient les resultats suivants sur le jeu de test :

- `MAE` : `13,207.95`
- `MSE` : `372,410,989.06`
- `RMSE` : `19,297.95`
- `R²` : `0.9301`

Ces valeurs proviennent de `entrainement_modele.ipynb` et peuvent varier si le modele est reentraine ou si le split des donnees change.

### Pourquoi `preprocess_ames` doit rester dans le code

Le notebook a serialize un pipeline qui reference explicitement `preprocess_ames`.

Donc meme si l'application ne l'appelle pas directement dans une ligne visible, elle est necessaire pour :

- charger correctement le pickle ;
- executer la transformation avant la prediction.

Si tu supprimes cette fonction, le chargement du modele peut echouer.

### Regenerer le modele

Si tu modifies l'entrainement, il faut :

1. ouvrir `entrainement_modele.ipynb` ;
2. reexecuter les cellules d'entrainement ;
3. resauvegarder le pipeline dans `model_pipeline_complet4.pkl` ;
4. redemarrer l'API.

### Attention a la compatibilite

Le modele actuel a ete sauvegarde avec une version donnee de scikit-learn.

Pour limiter les erreurs de compatibilite :

- garde une version stable de `scikit-learn` ;
- si tu reentraine le modele, regenere aussi le fichier `.pkl` avec le meme environnement cible.

## Variables d'environnement utiles

Les variables principales du projet sont :

- `FLASK_ENV`
- `FLASK_DEBUG`
- `FLASK_HOST`
- `PORT`
- `ENABLE_DB_RECORDING`
- `DATABASE_URL`
- `AUTO_CREATE_DB`
- `DB_POOL_RECYCLE`
- `MODEL_PATH`
- `MODEL_S3_URI`
- `MODEL_CACHE_DIR`
- `FRONTEND_ORIGINS`

Elles sont documentees dans `.env.example`.

## Fichiers importants

- `app.py` : point d'entree de l'application
- `config.py` : configuration
- `routes.py` : routes API
- `prediction_service.py` : logique de prediction
- `models.py` : modele de base de donnees
- `templates/index.html` : interface front
- `templates/app-config.js` : URL d'API pour le front
- `entrainement_modele.ipynb` : entrainement du modele
- `model_pipeline_complet4.pkl` : modele sauvegarde

## Notes pratiques

- si tu veux juste tester l'API, mets `ENABLE_DB_RECORDING=false` ;
- si tu actives la base, il faut une vraie `DATABASE_URL` ;
- si le front affiche une erreur JSON, verifie d'abord l'URL d'API dans `app-config.js` ;
- si le chargement du modele echoue, verifie la presence du fichier `.pkl` et la compatibilite de versions.
