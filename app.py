from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, date
from models import db, Patient, Vitals, GeneralAssessment, OverweightAssessment

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# ---------------- Helper Functions ----------------
def calculate_bmi(weight, height_cm):
    if height_cm <= 0:
        raise ValueError("Height must be greater than zero")
    height_m = height_cm / 100
    return round(weight / (height_m ** 2), 2)

def bmi_status(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    else:
        return "Overweight"

def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

# ---------------- Home ----------------
@app.route("/")
def home():
    return {"message": "Patient API running"}

# ---------------- Patient Registration ----------------
@app.route("/patients", methods=["POST"])
def register_patient():
    data = request.json

    required_fields = [
        "patient_id",
        "first_name",
        "last_name",
        "dob",
        "gender",
        "registration_date"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    if Patient.query.filter_by(patient_id=data["patient_id"]).first():
        return jsonify({"error": "Patient already registered"}), 400

    patient = Patient(
        patient_id=data["patient_id"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        dob=datetime.strptime(data["dob"], "%Y-%m-%d"),
        gender=data["gender"],
        registration_date=datetime.strptime(data["registration_date"], "%Y-%m-%d")
    )

    db.session.add(patient)
    db.session.commit()

    return jsonify({
        "message": "Patient registered successfully",
        "patient_id": patient.patient_id,
        "next_page": "vitals"
    }), 201


# ---------------- Vitals + BMI Logic ----------------
@app.route("/vitals", methods=["POST"])
def add_vitals():
    data = request.json
    required_fields = ["patient_id", "height", "weight", "visit_date"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    try:
        height = float(data["height"])
        weight = float(data["weight"])
        if height <= 0 or weight <= 0:
            return jsonify({"error": "Height and weight must be greater than zero"}), 400
        bmi = calculate_bmi(weight, height)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    vitals = Vitals(
        patient_id=data["patient_id"],
        visit_date=datetime.strptime(data["visit_date"], "%Y-%m-%d"),
        height=height,
        weight=weight,
        bmi=bmi
    )

    db.session.add(vitals)
    db.session.commit()

    next_form = "general" if bmi <= 25 else "overweight"

    return jsonify({
        "message": "Vitals saved",
        "bmi": bmi,
        "next_form": next_form,
        "vitals_id": vitals.id
    })

# ---------------- General Assessment ----------------
@app.route("/assessments/general", methods=["POST"])
def general_assessment():
    data = request.json
    required_fields = ["patient_id", "visit_date", "health", "drugs", "comments"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    assessment = GeneralAssessment(
        patient_id=data["patient_id"],
        visit_date=datetime.strptime(data["visit_date"], "%Y-%m-%d"),
        health=data["health"],
        drugs=data["drugs"],
        comments=data["comments"]
    )

    db.session.add(assessment)
    db.session.commit()

    return jsonify({"message": "General assessment saved", "assessment_id": assessment.id})

# ---------------- Overweight Assessment ----------------
@app.route("/assessments/overweight", methods=["POST"])
def overweight_assessment():
    data = request.json
    required_fields = ["patient_id", "visit_date", "health", "diet", "comments"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    assessment = OverweightAssessment(
        patient_id=data["patient_id"],
        visit_date=datetime.strptime(data["visit_date"], "%Y-%m-%d"),
        health=data["health"],
        diet=data["diet"],
        comments=data["comments"]
    )

    db.session.add(assessment)
    db.session.commit()

    return jsonify({"message": "Overweight assessment saved", "assessment_id": assessment.id})

# ---------------- Patient Listing ----------------
@app.route("/patients", methods=["GET"])
def list_patients():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    patients = Patient.query.all()
    results = []

    for p in patients:
        vitals_query = Vitals.query.filter_by(patient_id=p.patient_id)

        if start_date and end_date:
            vitals_query = vitals_query.filter(
                Vitals.visit_date.between(
                    datetime.strptime(start_date, "%Y-%m-%d"),
                    datetime.strptime(end_date, "%Y-%m-%d")
                )
            )

        latest_vitals = vitals_query.order_by(Vitals.visit_date.desc()).first()
        if not latest_vitals:
            continue

        results.append({
            "name": f"{p.first_name} {p.last_name}",
            "age": calculate_age(p.dob),
            "bmi": latest_vitals.bmi,
            "status": bmi_status(latest_vitals.bmi)
        })

    return jsonify(results)

# ---------------- Run Server ----------------
if __name__ == "__main__":
    app.run(debug=True)
