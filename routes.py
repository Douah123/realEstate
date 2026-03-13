from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from models import Prediction, db
from prediction_service import REQUIRED_FIELDS, build_model_input


def register_routes(app):
    @app.get("/")
    def home():
        return jsonify(
            {
                "ok": True,
                "message": "API de prediction immobiliere",
                "predict_url": "/predict",
                "method": "POST",
                "db_recording_enabled": app.config["ENABLE_DB_RECORDING"],
                "model_source": app.config["MODEL_S3_URI"] or app.config["RESOLVED_MODEL_PATH"],
            }
        )

    @app.get("/health")
    def health():
        return jsonify(
            {
                "ok": True,
                "status": "healthy",
                "db_recording_enabled": app.config["ENABLE_DB_RECORDING"],
            }
        )

    @app.post("/predict")
    def predict():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"ok": False, "error": "Le corps de la requete doit etre un JSON valide."}), 400

        missing_fields = [field for field in REQUIRED_FIELDS if payload.get(field) in (None, "")]
        if missing_fields:
            return jsonify({"ok": False, "error": f"Champs manquants: {', '.join(missing_fields)}"}), 400

        try:
            model_input = build_model_input(payload)
        except (TypeError, ValueError) as exc:
            return jsonify({"ok": False, "error": f"Donnees invalides: {exc}"}), 400

        prediction = float(app.config["PIPELINE"].predict(model_input)[0])
        prediction_id = None

        if app.config["ENABLE_DB_RECORDING"]:
            prediction_record = Prediction(
                qualite_generale=int(payload["qualite_generale"]),
                surface_habitable=float(payload["surface_habitable"]),
                surface_totale_sous_sol=float(payload["surface_totale_sous_sol"]),
                surface_garage=float(payload["surface_garage"]),
                surface_terrain=float(payload["surface_terrain"]),
                annee_construction=int(payload["annee_construction"]),
                total_salles_bain=float(payload["total_salles_bain"]),
                climatisation_centrale=str(payload["climatisation_centrale"]).lower(),
                prediction=prediction,
            )

            try:
                db.session.add(prediction_record)
                db.session.commit()
                prediction_id = prediction_record.id
            except SQLAlchemyError as exc:
                db.session.rollback()
                return jsonify({"ok": False, "error": f"Erreur base de donnees: {exc.__class__.__name__}"}), 500

        return jsonify(
            {
                "ok": True,
                "prediction": prediction,
                "prediction_text": f"Prix predit : {prediction:,.0f} $",
                "prediction_id": prediction_id,
            }
        )
