from pathlib import Path
from urllib.parse import urlparse

import joblib
import pandas as pd

try:
    import boto3
except ImportError:  # pragma: no cover
    boto3 = None


REQUIRED_FIELDS = [
    "qualite_generale",
    "surface_habitable",
    "surface_totale_sous_sol",
    "surface_garage",
    "surface_terrain",
    "annee_construction",
    "total_salles_bain",
    "climatisation_centrale",
]


def preprocess_ames(df):
    df = df.copy()
    df["Age_maison"] = df["Annee_vente"] - df["Annee_construction"]
    df["Surface_totale"] = (
        df["Surface_1er_etage"]
        + df["Surface_2eme_etage"]
        + df["Surface_totale_sous_sol"]
    )

    if "Total_salles_bain" not in df.columns:
        df["Total_salles_bain"] = (
            df["Salle_bain_complete"]
            + 0.5 * df["Demi_salle_bain"]
            + df["Salle_bain_complete_sous_sol"]
            + 0.5 * df["Demi_salle_bain_sous_sol"]
        )

    df["Surface_totale_porche"] = (
        df["Surface_porche_ouvert"]
        + df["Porche_ferme"]
        + df["Porche_trois_saisons"]
        + df["Porche_moustiquaire"]
    )
    df["Surface_totale_exterieure"] = (
        df["Surface_terrasse_bois"] + df["Surface_totale_porche"]
    )

    if "Climatisation_centrale" in df.columns:
        df["Climatisation_centrale_y"] = (
            df["Climatisation_centrale"].astype(str).str.lower() == "y"
        ).astype(int)

    if "Zone_urbaine" in df.columns:
        df["Zone_urbaine_rm"] = (
            df["Zone_urbaine"].astype(str).str.lower() == "rm"
        ).astype(int)

    colonnes_finales = [
        "Qualite_generale",
        "Surface_habitable",
        "Surface_totale",
        "Annee_construction",
        "Surface_totale_sous_sol",
        "Surface_finie_sous_sol_1",
        "Qualite_sous_sol",
        "Surface_garage",
        "Surface_terrain",
        "Surface_1er_etage",
        "Annee_renovation",
        "Qualite_cuisine",
        "Total_salles_bain",
        "Capacite_garage_voitures",
        "Climatisation_centrale_y",
        "Surface_sous_sol_non_finie",
        "Etat_general",
        "Annee_construction_garage",
        "Surface_totale_exterieure",
        "Age_maison",
        "Zone_urbaine_rm",
        "Facade_terrain",
    ]

    return df.reindex(columns=colonnes_finales, fill_value=0)


def download_model_from_s3(s3_uri, target_dir):
    if boto3 is None:
        raise RuntimeError("boto3 est requis pour charger le modele depuis S3.")

    parsed = urlparse(s3_uri)
    if parsed.scheme != "s3" or not parsed.netloc or not parsed.path:
        raise ValueError("MODEL_S3_URI doit etre au format s3://bucket/key")

    bucket = parsed.netloc
    key = parsed.path.lstrip("/")
    target_dir.mkdir(parents=True, exist_ok=True)
    destination = target_dir / Path(key).name

    if not destination.exists():
        boto3.client("s3").download_file(bucket, key, str(destination))

    return destination


def resolve_model_path(app):
    s3_uri = app.config.get("MODEL_S3_URI")
    if s3_uri:
        cache_dir = Path(app.config["MODEL_CACHE_DIR"])
        return download_model_from_s3(s3_uri, cache_dir)

    model_path = Path(app.config["MODEL_PATH"])
    if not model_path.is_absolute():
        model_path = Path(app.root_path) / model_path
    return model_path


def load_pipeline(app):
    model_path = resolve_model_path(app)
    app.config["RESOLVED_MODEL_PATH"] = str(model_path)
    return joblib.load(model_path)


def build_model_input(payload):
    qualite_generale = int(payload["qualite_generale"])
    surface_habitable = float(payload["surface_habitable"])
    surface_totale_sous_sol = float(payload["surface_totale_sous_sol"])
    surface_garage = float(payload["surface_garage"])
    surface_terrain = float(payload["surface_terrain"])
    annee_construction = int(payload["annee_construction"])
    total_salles_bain = float(payload["total_salles_bain"])
    climatisation_centrale = str(payload["climatisation_centrale"]).lower()

    surface_1er_etage = surface_habitable
    surface_2eme_etage = 0
    surface_finie_sous_sol_1 = 0.5 * surface_totale_sous_sol
    surface_sous_sol_non_finie = 0.5 * surface_totale_sous_sol
    qualite_sous_sol = max(3, min(qualite_generale, 7))
    qualite_cuisine = max(4, min(qualite_generale, 8))
    capacite_garage_voitures = max(0, min(4, round(surface_garage / 180)))

    if annee_construction >= 2000:
        etat_general = 6
    elif annee_construction >= 1970:
        etat_general = 5
    else:
        etat_general = 4

    return pd.DataFrame(
        [
            {
                "Qualite_generale": qualite_generale,
                "Surface_habitable": surface_habitable,
                "Surface_1er_etage": surface_1er_etage,
                "Surface_2eme_etage": surface_2eme_etage,
                "Surface_totale_sous_sol": surface_totale_sous_sol,
                "Surface_finie_sous_sol_1": surface_finie_sous_sol_1,
                "Qualite_sous_sol": qualite_sous_sol,
                "Surface_garage": surface_garage,
                "Surface_terrain": surface_terrain,
                "Annee_renovation": annee_construction,
                "Qualite_cuisine": qualite_cuisine,
                "Total_salles_bain": total_salles_bain,
                "Capacite_garage_voitures": capacite_garage_voitures,
                "Climatisation_centrale": climatisation_centrale,
                "Surface_sous_sol_non_finie": surface_sous_sol_non_finie,
                "Etat_general": etat_general,
                "Annee_construction_garage": annee_construction,
                "Facade_terrain": round(max(40, min(120, (surface_terrain / 2) ** 0.5))),
                "Annee_vente": 2010,
                "Annee_construction": annee_construction,
                "Zone_urbaine": "rl",
                "Surface_terrasse_bois": 0,
                "Surface_porche_ouvert": 0,
                "Porche_ferme": 0,
                "Porche_trois_saisons": 0,
                "Porche_moustiquaire": 0,
            }
        ]
    )
