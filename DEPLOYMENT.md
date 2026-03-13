# Deploiement AWS

## Backend

Le backend expose une API Flask dans `app.py` et un point d'entree WSGI dans `wsgi.py`.

Variables d'environnement minimales :

```env
ENABLE_DB_RECORDING=true
DATABASE_URL=mysql+pymysql://username:password@your-rds-endpoint:3306/predict
MODEL_S3_URI=s3://your-bucket/models/model_pipeline_complet4.pkl
FRONTEND_ORIGINS=https://your-frontend.s3-website-region.amazonaws.com,https://www.your-domain.com
```

Si le modele est present localement sur l'instance, utilise `MODEL_PATH` au lieu de `MODEL_S3_URI`.

## RDS

La table `predictions` est definie dans `models.py`.

Initialisation manuelle :

```bash
flask --app app init-db
```

N'active `AUTO_CREATE_DB=true` que pour un bootstrap simple.

## Frontend S3

Le fichier HTML peut etre servi statiquement depuis S3/CloudFront.

Comportement de resolution de l'API :

1. `window.APP_CONFIG.apiBaseUrl` si defini
2. `localStorage.api_base_url` si defini
3. `http://127.0.0.1:5000` en local
4. `https://api.example.com` en fallback production

Pour la prod, cree un fichier `app-config.js` a cote du HTML :

```js
window.APP_CONFIG = {
  apiBaseUrl: "https://api.your-domain.com"
};
```

## Gunicorn

Commande de demarrage :

```bash
gunicorn wsgi:app --bind 0.0.0.0:8000 --workers 2 --timeout 120
```
