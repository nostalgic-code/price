import logging
from flask import Flask, request, jsonify
import requests
import json
from requests.auth import HTTPBasicAuth

# Configure logging
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

# Configuration
USERNAME = "d5900938-be95-4412-95b3-50b11983e13e"
PASSWORD = "90fa0de5-250a-4e99-bd65-85b1854d9c82"
PRICE_URL = "http://102.33.60.228:9183/getResources/subroutine/pricing"
DEFAULT_LOCATION = "101"

# Initialize Flask application


@app.route('/get_price/<item_code>', methods=['GET'])
def get_price(item_code):
    """
    Gets price and quantity for a given stock code using the pricing subroutine.
    """
    logging.debug(f"Received request for item_code: {item_code}")

    payload = {
        "item": item_code,
        "location": DEFAULT_LOCATION
    }

    try:
        logging.debug(f"Sending request to {PRICE_URL} with payload: {payload}")

        res = requests.post(
            PRICE_URL,
            json=payload,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            headers={"Accept": "application/json"},
            timeout=15
        )

        logging.debug(f"Response status code: {res.status_code}")
        logging.debug(f"Response text: {res.text}")

        if res.status_code == 200:
            data = res.json()
            logging.debug(f"Parsed response JSON: {data}")

            # The response is double-encoded JSON string inside response->success
            if 'response' in data and 'success' in data['response']:
                nested = json.loads(data['response']['success'])

                logging.debug(f"Extracted nested JSON: {nested}")

                return jsonify({
                    "item": nested.get("item"),
                    "price": nested.get("price"),
                    "quantity": nested.get("qty_available")
                }), 200
            else:
                logging.error("Unexpected response format.")
                return jsonify({"error": "Unexpected response format", "raw": data}), 500
        else:
            logging.error(f"HTTP {res.status_code}: {res.reason}")
            return jsonify({
                "error": f"HTTP {res.status_code}",
                "message": res.reason,
                "details": res.text
            }), res.status_code

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {str(e)}")
        return jsonify({"error": "Request failed", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
