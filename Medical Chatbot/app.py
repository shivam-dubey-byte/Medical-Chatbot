
from flask import Flask, request, jsonify
import requests
import logging
from functools import lru_cache
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define API URLs
RX_NORM_API_URL = "https://rxnav.nlm.nih.gov/REST"
OPEN_FDA_API_URL = "https://api.fda.gov/drug/event.json"
PILLBOX_API_URL = "https://pillbox.nlm.nih.gov/api"

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
        response.raise_for_status()
        data = response.json()
        if "idGroup" in data and "rxnormId" in data["idGroup"]:
            return data["idGroup"]["rxnormId"][0]
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

@lru_cache(maxsize=100)
def get_drug_interactions(rxcui):
    """
    Fetch drug interactions using the RxCUI.
    """
    url = f"{RX_NORM_API_URL}/interaction/interaction.json?rxcui={rxcui}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "interactionTypeGroup" in data:
            return data["interactionTypeGroup"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching drug interactions for RxCUI {rxcui}: {e}")
    return None

@lru_cache(maxsize=100)
def get_side_effects(drug_name):
    """
    Fetch side effects using the OpenFDA API.
    """
    url = f"{OPEN_FDA_API_URL}?search=patient.drug.medicinalproduct:{drug_name}&count=patient.reaction.reactionmeddrapt.exact"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "results" in data:
            return [result["term"] for result in data["results"]]
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching side effects for {drug_name}: {e}")
    return None

@lru_cache(maxsize=100)
def get_dosage_info(rxcui):
    """
    Fetch dosage information using the RxCUI.
    """
    url = f"{RX_NORM_API_URL}/rxcui/{rxcui}/ndcstatus.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "ndcStatus" in data:
            return data["ndcStatus"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching dosage info for RxCUI {rxcui}: {e}")
    return None

@lru_cache(maxsize=100)
def get_drug_images(drug_name):
    """
    Fetch drug images using the Pillbox API.
    """
    url = f"{PILLBOX_API_URL}/search.json?name={drug_name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "results" in data:
            return [result["image_url"] for result in data["results"]]
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching drug images for {drug_name}: {e}")
    return None

def get_alternatives(drug_name):
    """
    Fetch alternative medicines for a given drug.
    """
    return alternatives_data.get(drug_name, [])

def generate_layman_response(details, related_drugs, alternatives, interactions, side_effects, dosage_info, images):
    """
    Generate a layman-friendly response from drug details, related drugs, alternatives, interactions, side effects, dosage info, and images.
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

    # Add interactions
    if interactions:
        response.append("**Interactions:**")
        for group in interactions:
            for interaction in group["interactionType"]:
                for pair in interaction["interactionPair"]:
                    response.append(f"- **{pair['interactionConcept'][0]['sourceConceptItem']['name']}** interacts with **{pair['interactionConcept'][1]['sourceConceptItem']['name']}**: {pair['description']}")

    # Add side effects
    if side_effects:
        response.append("**Side Effects:**")
        response.append(f"Common side effects include **{', '.join(side_effects)}**.")

    # Add dosage info
    if dosage_info:
        response.append("**Dosage Information:**")
        response.append(f"Dosage details: **{dosage_info.get('description', 'Not available')}**.")

    # Add drug images
    if images:
        response.append("**Drug Images:**")
        for image_url in images:
            response.append(f"![Drug Image]({image_url})")

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

    # Fetch all drug-related data
    details = get_drug_details(rxcui)
    related_drugs = get_related_drugs(rxcui)
    alternatives = get_alternatives(drug_name)
    interactions = get_drug_interactions(rxcui)
    side_effects = get_side_effects(drug_name)
    dosage_info = get_dosage_info(rxcui)
    images = get_drug_images(drug_name)

    if not details and not related_drugs and not alternatives and not interactions and not side_effects and not dosage_info and not images:
        return jsonify({"error": f"No details found for {drug_name}."}), 404

    # Generate a layman-friendly response
    layman_response = generate_layman_response(details, related_drugs, alternatives, interactions, side_effects, dosage_info, images)
    return jsonify({
        "drug_name": drug_name,
        "rxcui": rxcui,
        "response": layman_response
    })

if __name__ == "__main__":
    app.run(debug=True)