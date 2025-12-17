const backendUrl = "http://127.0.0.1:5000";

document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.getElementById("registerForm");
    if (!registerForm) return;

    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const patient_id = document.getElementById("patient_id").value;
        const first_name = document.getElementById("first_name").value;
        const last_name = document.getElementById("last_name").value;
        const dob = document.getElementById("dob").value;
        const gender = document.getElementById("gender").value;
        const registration_date = document.getElementById("registration_date").value;

        const response = await fetch(`${backendUrl}/patients`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                patient_id,
                first_name,
                last_name,
                dob,
                gender,
                registration_date
            })
        });

        const result = await response.json();
        console.log("REGISTER RESPONSE:", result);

        if (response.ok) {
            window.location.href = `vitals.html?patient_id=${result.patient_id}`;
        } else {
            alert(result.error);
        }
    });
});



// --------------------------
// Save Vitals
// --------------------------
const backendUrl = "http://127.0.0.1:5000";

// -----------------------------------
// AUTO-FILL PATIENT ID FROM URL
// -----------------------------------
const params = new URLSearchParams(window.location.search);
const urlPatientId = params.get("patient_id");

if (urlPatientId && document.getElementById("patientId")) {
    document.getElementById("patientId").value = urlPatientId;
}

// -----------------------------------
// VITALS FORM SUBMISSION
// -----------------------------------
const vitalsForm = document.getElementById("vitalsForm");

if (vitalsForm) {
    vitalsForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const patient_id = document.getElementById("patientId").value;
        const height = document.getElementById("height").value;
        const weight = document.getElementById("weight").value;
        const visit_date = document.getElementById("visit_date").value;

        try {
            const response = await fetch(`${backendUrl}/vitals`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    patient_id,
                    height,
                    weight,
                    visit_date
                })
            });

            const result = await response.json();

            if (response.ok) {
                alert(`Vitals saved successfully.\nBMI: ${result.bmi}`);

                // ✅ REDIRECT BASED ON BMI
                if (result.next_form === "general") {
                    window.location.href = `general.html?patient_id=${patient_id}&visit_date=${visit_date}`;
                } else {
                    window.location.href = `overweight.html?patient_id=${patient_id}&visit_date=${visit_date}`;
                }

            } else {
                alert(result.error || "Failed to save vitals");
            }

        } catch (error) {
            console.error(error);
            alert("Error connecting to backend");
        }
    });
}


// Run access check on page load
document.addEventListener("DOMContentLoaded", () => {
    // Retrieve BMI stored from vitals page
    const bmi = parseFloat(localStorage.getItem("bmi"));

    if (!bmi) {
        alert("BMI not found. Please enter vitals first.");
        window.location.href = "vitals.html";
        return;
    }

    if (bmi <= 25) {
        alert("Access denied: This form is only for patients with BMI > 25.");
        window.location.href = "patients.html";
    }
});

const overweightForm = document.getElementById("overweightForm");

if (overweightForm) {
    overweightForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const patient_id = document.getElementById("patientId").value;
        const visit_date = document.getElementById("visit_date").value;
        const health = document.getElementById("health").value;
        const diet = document.getElementById("diet").value;
        const comments = document.getElementById("comments").value;

        // Mandatory field check
        if (!patient_id || !visit_date || !health || !diet || !comments) {
            alert("All fields are required!");
            return;
        }

        try {
            const response = await fetch(`${backendUrl}/assessments/overweight`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ patient_id, visit_date, health, diet, comments })
            });

            const result = await response.json();
            console.log(result);

            if (response.ok) {
                alert(result.message || "Overweight assessment saved");

                // ✅ Redirect after save
                window.location.href = "patients.html";
            } else {
                alert(result.error || "Failed to save assessment");
            }

        } catch (err) {
            console.error(err);
            alert("Error connecting to backend");
        }
    });
}



// --------------------------
// Save General Info
// --------------------------
// Run access check on page load
document.addEventListener("DOMContentLoaded", () => {
    // Retrieve BMI stored from vitals page
    const bmi = parseFloat(localStorage.getItem("bmi"));

    if (!bmi) {
        alert("BMI not found. Please enter vitals first.");
        window.location.href = "vitals.html";
        return;
    }

    if (bmi > 25) {
        alert("Access denied: This form is only for patients with BMI ≤ 25.");
        window.location.href = "patients.html";
    }
});

const generalForm = document.getElementById("generalForm");

if (generalForm) {
    generalForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const patient_id = document.getElementById("patientId").value;
        const health = document.getElementById("health").value;
        const drugs = document.getElementById("drugs").value;
        const comments = document.getElementById("comments").value;
        const visit_date = new Date().toISOString().split("T")[0]; // today

        // Mandatory field check
        if (!patient_id || !health || !drugs || !comments) {
            alert("All fields are required!");
            return;
        }

        try {
            const response = await fetch(`${backendUrl}/assessments/general`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ patient_id, health, drugs, comments, visit_date })
            });

            const result = await response.json();
            console.log(result);

            if (response.ok) {
                alert(result.message || "General assessment saved");

                // ✅ Redirect to Patient Listing after save
                window.location.href = "patients.html";
            } else {
                alert(result.error || "Failed to save assessment");
            }
        } catch (err) {
            console.error(err);
            alert("Error connecting to backend");
        }
    });
}

// --------------------------
// Fetch Patients
// --------------------------
const backendUrl = "http://127.0.0.1:5000";

// Render patients into table
function renderPatients(patients) {
    const tbody = document.getElementById("patientsBody");
    tbody.innerHTML = ""; // clear table

    patients.forEach(patient => {
        const age = calculateAge(patient.date_of_birth);
        const bmi = patient.last_bmi;
        const classification = classifyBMI(bmi);

        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${patient.first_name} ${patient.last_name}</td>
            <td>${age}</td>
            <td>${bmi.toFixed(1)}</td>
            <td>${classification}</td>
        `;
        tbody.appendChild(row);
    });
}

// BMI Classification
function classifyBMI(bmi) {
    if (bmi < 18.5) return "Underweight";
    if (bmi >= 18.5 && bmi <= 24.9) return "Normal";
    return "Overweight";
}

// Calculate age from DOB
function calculateAge(dob) {
    const birthDate = new Date(dob);
    const diff = Date.now() - birthDate.getTime();
    const age = new Date(diff).getUTCFullYear() - 1970;
    return age;
}

// Fetch all patients or filter by date
function fetchPatients(date = "") {
    let url = `${backendUrl}/patients`;
    if (date) url += `?visit_date=${date}`;

    fetch(url)
        .then(res => res.json())
        .then(renderPatients)
        .catch(err => console.error(err));
}

// Filter button handler
function filterPatients() {
    const date = document.getElementById("filterDate").value;
    fetchPatients(date);
}

// Initial load
fetchPatients();
