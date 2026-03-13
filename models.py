from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()


class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    qualite_generale = db.Column(db.Integer, nullable=False)
    surface_habitable = db.Column(db.Float, nullable=False)
    surface_totale_sous_sol = db.Column(db.Float, nullable=False)
    surface_garage = db.Column(db.Float, nullable=False)
    surface_terrain = db.Column(db.Float, nullable=False)
    annee_construction = db.Column(db.Integer, nullable=False)
    total_salles_bain = db.Column(db.Float, nullable=False)
    climatisation_centrale = db.Column(db.String(5), nullable=False)
    prediction = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
