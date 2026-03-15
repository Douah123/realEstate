# Deployment Guide – Real Estate Price Prediction (AWS)

Ce document décrit les étapes nécessaires pour déployer l’application de prédiction immobilière sur AWS.

L’architecture utilisée est :

Frontend (HTML/CSS) → S3  
API Flask → EC2  
Base de données MySQL → RDS  
Monitoring → CloudWatch  

---

# 1. Création du VPC

Un VPC dédié a été créé pour isoler l’infrastructure réseau.

Configuration :

CIDR : 10.0.0.0/16

Sous-réseaux :

Public Subnet  
10.0.1.0/24  
Utilisé pour l’instance EC2

Private Subnet  
10.0.2.0/24  
Utilisé pour la base de données RDS

Private Subnet  
10.0.3.0/24  
Utilisé pour la base de données RDS

Composants réseau :

Internet Gateway attaché au VPC  
Route Table publique permettant l’accès Internet pour EC2

Objectif :  
Séparer les ressources publiques et privées pour des raisons de sécurité.

---

# 2. Configuration des Security Groups

Deux Security Groups ont été créés.

EC2-SG

Autorise :

Port 22 (SSH) uniquement depuis l’IP personnelle  
Port 80 (HTTP) public  
Port 443 (HTTPS) public  
Port 8000 pour l’API Flask

Objectif :  
Permettre l’accès à l’API et l’administration SSH.

---

RDS-SG

Autorise :

Port 3306 (MySQL) uniquement depuis EC2-SG

Objectif :  
Empêcher tout accès direct à la base de données depuis Internet.

---

# 3. Entraînement du modèle Machine Learning

Dataset utilisé :

Ames Housing Dataset (Kaggle)

Étapes réalisées :

Nettoyage des données  
Feature Engineering  
Création de nouvelles variables  
Entraînement du modèle de régression

Modèle utilisé :

RandomForestRegressor (Scikit-learn)

Évaluation :

RMSE   
R²

Objectif :  
Prédire le prix d’un bien immobilier à partir de caractéristiques principales.

---

# 4. Sérialisation du modèle et stockage S3

Le modèle entraîné a été sauvegardé avec Joblib.

Fichier :

model_pipeline_complet4.pkl

Le fichier est uploadé dans un bucket S3.

Objectif :

Permettre à l’instance EC2 de récupérer le modèle automatiquement.

Accès sécurisé via IAM Role (aucune clé AWS stockée dans le code).

---

# 5. Déploiement de l’API Flask sur EC2

Instance EC2 :

Type : t2.micro  
OS : Ubuntu  

Étapes :

Clonage du repository GitHub

Installation des dépendances

pip install -r requirements.txt

Configuration des variables d’environnement (.env)

Lancement de l’API

gunicorn -w 2 -b 0.0.0.0:8000 app:app

Endpoint principal :

POST /predict

Exemple de requête JSON :

{
  "qualite_generale": 6,
  "surface_habitable": 1500,
  "surface_totale_sous_sol": 800,
  "surface_garage": 300,
  "surface_terrain": 5000,
  "annee_construction": 2005,
  "total_salles_bain": 2,
  "climatisation_centrale": "y"
}

Objectif :

Exposer un service API permettant d’effectuer des prédictions.

---

# 6. Base de données RDS MySQL

Service utilisé :

Amazon RDS – MySQL

Instance :

db.t3.micro

Base créée :

predict

Table :

predictions

Colonnes :

id  
qualite_generale  
surface_habitable  
surface_totale_sous_sol  
surface_garage  
surface_terrain  
annee_construction  
total_salles_bain  
climatisation_centrale  
prediction  
created_at  

Objectif :

Enregistrer chaque prédiction réalisée par l’API.

---

# 7. Frontend statique sur S3

Une interface HTML/CSS simple permet de saisir les caractéristiques du bien.

Fonctionnement :

Formulaire utilisateur  
Envoi d’une requête POST vers l’API EC2  
Affichage du prix prédit

Le site est hébergé via :

S3 Static Website Hosting.

Objectif :

Fournir une interface utilisateur simple pour interagir avec l’API.

---

# 8. Monitoring avec CloudWatch

CloudWatch est utilisé pour surveiller l’instance EC2.

Alarme créée :

CPUUtilization > 80%

Configuration :

Metric : CPUUtilization  
Period : 5 minutes  
Statistic : Average  

Objectif :

Être alerté en cas de forte utilisation CPU.

---

# Architecture finale

Frontend (S3 Static Website)

↓

API Flask (EC2)

↓

Modèle ML chargé depuis S3

↓

Base de données MySQL (RDS)

↓

Monitoring CloudWatch

---

# Conclusion

Cette architecture démontre l’intégration complète d’un modèle de Machine Learning dans une infrastructure Cloud AWS.

Services AWS utilisés :

VPC  
EC2  
S3  
RDS  
CloudWatch  

L’application permet de prédire le prix d’un bien immobilier via une API REST et de stocker les résultats dans une base de données.