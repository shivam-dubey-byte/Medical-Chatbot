from flask import Flask, request, jsonify
import requests
import logging
from functools import lru_cache

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the RxNorm API base URL
RX_NORM_API_URL = "https://rxnav.nlm.nih.gov/REST"

# Define alternative medicine data
alternatives_data = {
    "Metformin": ["Glucophage", "Fortamet"],
    "Ibuprofen": ["Advil", "Motrin"],
    "Omeprazole": ["Prilosec", "Zegerid"]
}

# Cache API responses to reduce redundant calls
@lru_cache(maxsize=100)
def get_rxcui(drug_name):
    """
    Get the RxCUI for a drug by its name.
    """
    url = f"{RX_NORM_API_URL}/rxcui.json?name={drug_name}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        if "idGroup" in data and "rxnormId" in data["idGroup"]:
            return data["idGroup"]["rxnormId"][0]  # Return the first RxCUI
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching RxCUI for {drug_name}: {e}")
    return None

@lru_cache(maxsize=100)
def get_drug_details(rxcui):
    """
    Get detailed information about a drug using its RxCUI.
    """
    url = f"{RX_NORM_API_URL}/rxcui/{rxcui}/properties.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "properties" in data:
            return data["properties"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching drug details for RxCUI {rxcui}: {e}")
    return None

@lru_cache(maxsize=100)
def get_related_drugs(rxcui):
    """
    Fetch related drugs using the RxCUI.
    """
    url = f"{RX_NORM_API_URL}/rxcui/{rxcui}/allrelated.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "allRelatedGroup" in data and "conceptGroup" in data["allRelatedGroup"]:
            return data["allRelatedGroup"]["conceptGroup"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching related drugs for RxCUI {rxcui}: {e}")
    return None

def get_alternatives(drug_name):
    """
    Fetch alternative medicines for a given drug.
    """
    return alternatives_data.get(drug_name, [])

def generate_layman_response(details, related_drugs, alternatives):
    """
    Generate a layman-friendly response from drug details, related drugs, and alternatives.
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

    # Add alternatives
    if alternatives:
        response.append("**Alternatives:**")
        response.append(f"Alternative medicines include **{', '.join(alternatives)}**.")

    return "\n".join(response)

@app.route("/drug-info", methods=["POST"])
def get_drug_info():
    """
    Endpoint to fetch drug information.
    """
    # Get JSON data from the request
    data = request.get_json()
    if not data or "drug_name" not in data:
        return jsonify({"error": "Please provide a drug name in JSON format."}), 400
    
    drug_name = data["drug_name"]
    logger.info(f"Fetching information for drug: {drug_name}")

    # Get RxCUI for the drug
    rxcui = get_rxcui(drug_name)
    if not rxcui:
        return jsonify({"error": f"Could not find RxCUI for {drug_name}."}), 404

    # Fetch drug details, related drugs, and alternatives
    details = get_drug_details(rxcui)
    related_drugs = get_related_drugs(rxcui)
    alternatives = get_alternatives(drug_name)

    if not details and not related_drugs and not alternatives:
        return jsonify({"error": f"No details found for {drug_name}."}), 404

    # Generate a layman-friendly response
    layman_response = generate_layman_response(details, related_drugs, alternatives)
    return jsonify({
        "drug_name": drug_name,
        "rxcui": rxcui,
        "response": layman_response
    })

if __name__ == "__main__":
    app.run(debug=True)