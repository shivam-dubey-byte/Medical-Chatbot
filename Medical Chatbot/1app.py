from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Define the RxNorm API base URL
RX_NORM_API_URL = "https://rxnav.nlm.nih.gov/REST"

def get_rxcui(drug_name):
    """
    Get the RxCUI for a drug by its name.
    """
    url = f"{RX_NORM_API_URL}/rxcui.json?name={drug_name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "idGroup" in data and "rxnormId" in data["idGroup"]:
            return data["idGroup"]["rxnormId"][0]  # Return the first RxCUI
    return None

def get_drug_details(rxcui):
    """
    Get detailed information about a drug using its RxCUI.
    """
    url = f"{RX_NORM_API_URL}/rxcui/{rxcui}/properties.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "properties" in data:
            return data["properties"]
    return None

def get_related_drugs(rxcui):
    """
    Fetch related drugs using the RxCUI.
    """
    url = f"{RX_NORM_API_URL}/rxcui/{rxcui}/allrelated.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "allRelatedGroup" in data and "conceptGroup" in data["allRelatedGroup"]:
            return data["allRelatedGroup"]["conceptGroup"]
    return None

def generate_layman_response(details, related_drugs):
    """
    Generate a layman-friendly response from drug details and related drugs.
    """
    response = []

    # Add drug details
    if details:
        response.append(f"The drug **{details.get('name', 'Unknown')}** is used for **{details.get('indication', 'various conditions')}**.")
        if "synonym" in details and details["synonym"]:
            response.append(f"It is also known as **{details['synonym']}**.")

    # Add related drugs
    if related_drugs:
        related_drugs_by_type = {}
        for group in related_drugs:
            if "conceptProperties" in group:
                for concept in group["conceptProperties"]:
                    tty = concept["tty"]
                    name = concept["name"]
                    if tty not in related_drugs_by_type:
                        related_drugs_by_type[tty] = []
                    related_drugs_by_type[tty].append(name)

        # Brand Names
        if "BN" in related_drugs_by_type:
            brand_names = related_drugs_by_type["BN"]
            response.append(f"This drug is also sold under the brand name(s): **{', '.join(brand_names)}**.")

        # Ingredients
        if "IN" in related_drugs_by_type:
            ingredients = related_drugs_by_type["IN"]
            response.append(f"The active ingredient in this drug is **{', '.join(ingredients)}**.")

        # Precise Ingredients
        if "PIN" in related_drugs_by_type:
            precise_ingredients = related_drugs_by_type["PIN"]
            response.append(f"The precise form of the active ingredient is **{', '.join(precise_ingredients)}**.")

        # Dose Forms
        if "DF" in related_drugs_by_type:
            dose_forms = related_drugs_by_type["DF"]
            response.append(f"This drug is available as **{', '.join(dose_forms)}**.")

        # Dose Form Groups
        if "DFG" in related_drugs_by_type:
            dose_form_groups = related_drugs_by_type["DFG"]
            response.append(f"It comes in forms like **{', '.join(dose_form_groups)}**.")

    return "\n".join(response)

@app.route("/drug-info", methods=["POST"])
def get_drug_info():
    # Get JSON data from the request
    data = request.get_json()
    if not data or "drug_name" not in data:
        return jsonify({"error": "Please provide a drug name in JSON format."}), 400
    
    drug_name = data["drug_name"]
    rxcui = get_rxcui(drug_name)
    if rxcui:
        details = get_drug_details(rxcui)
        related_drugs = get_related_drugs(rxcui)
        if details or related_drugs:
            layman_response = generate_layman_response(details, related_drugs)
            return jsonify({
                "drug_name": drug_name,
                "rxcui": rxcui,
                "response": layman_response
            })
    return jsonify({"error": "No details found for this drug."}), 404

if __name__ == "__main__":
    app.run(debug=True)