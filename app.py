'''
Hi, 

I built this webservie using python Flask to process receipts and get award points with four functions.
process_receipt(): process input data 
get_points(receipt_id): output the calculated point number and send it back
calculate_points(receipt_data): build basic rules for gaining points
validate_receipt(receipt_data): validate input data, check if every field is valid, to prevent potential threats
'''
from flask import Flask, request, jsonify
import re,math
from datetime import datetime, time
import uuid
app = Flask(__name__)

# In-memory storage for receipts and points
receipts = {}
points = {}

'''
Jobs of this POST route:
(1)takes in a JSON receipt 
(2)calculate the award points based on the JSONreceipt
(3)returns a JSON object with an ID generated by your code.
'''
@app.route('/receipts/process', methods=['POST'])
def process_receipt(): 
    receipt_data = request.json 

    # Validate the receipt data against the schema
    valid, error_field, error_reason = validate_receipt(receipt_data)
    if not valid:
        return jsonify({"error": f"Invalid receipt data. Field '{error_field}' has error: {error_reason}"}), 400

    # Generate a unique ID for the receipt
    receipt_id = str(uuid.uuid4())
    receipts[receipt_id] = receipt_data

    # Calculate points based on the provided logic
    awarded_points = calculate_points(receipt_data)
    points[receipt_id] = awarded_points
    return jsonify({"id": receipt_id}), 200

'''
Jobs of this Get route
(1)search the value in points dictionary according to the id provided through url as a key
(2)throw an error if wrong id provided
'''
@app.route('/receipts/<string:receipt_id>/points', methods=['GET'])
def get_points(receipt_id):
    if receipt_id in points:
        awarded_points = points[receipt_id]
        return jsonify({"points": awarded_points}), 200
    else:
        return jsonify({"error": "Receipt not found"}), 404

'''
Jobs of this calculation function following with the setting rules.
'''
def calculate_points(receipt_data):
    #Initiate point 
    awarded_points = 0

    # Calculate points for retailer name
    retailer_name = receipt_data["retailer"]
    awarded_points += len(re.sub(r'[^a-zA-Z0-9]', '', retailer_name)) #select all alphanumeric characters

    # Calculate points for total amount
    total_amount = float(receipt_data["total"])
    # Find if the total is a round dollar amount
    if total_amount.is_integer():
        awarded_points += 50
    # Find if the total is a multiple of 0.25
    if total_amount % 0.25 == 0:
        awarded_points += 25

    # Calculate points for number of items
    num_items = len(receipt_data["items"])
    awarded_points += (num_items // 2) * 5

    # Calculate points for item description length
    for item in receipt_data["items"]:
        description_length = len(item["shortDescription"].strip())
        if description_length % 3 == 0:
            price = float(item["price"])
            item_points = math.ceil(price * 0.2)
            awarded_points += item_points

    # Parse purchase date and time using datetime
    purchase_date = datetime.strptime(receipt_data["purchaseDate"], "%Y-%m-%d")
    purchase_time = datetime.strptime(receipt_data["purchaseTime"], "%H:%M").time()

    if purchase_date.day % 2 != 0:
        awarded_points += 6

    # Assuming the time range will not include 2:00 pm and 4:00 pm
    if time(14) < purchase_time < time(16):
        awarded_points += 10

    return awarded_points

#validate input receipt data


def validate_receipt(receipt_data):
    # Validate retailer
    retailer = receipt_data.get("retailer")
    if not retailer or not re.match(r"^.*\S.*$", retailer):
        return False, "retailer", "Invalid retailer name"

    # Validate purchaseDate using datetime
    purchase_date = receipt_data.get("purchaseDate")
    try:
        datetime.strptime(purchase_date, "%Y-%m-%d")
    except ValueError:
        return False, "purchaseDate", "Invalid purchase date"

    # Validate purchaseTime using datetime
    purchase_time = receipt_data.get("purchaseTime")
    try:
        datetime.strptime(purchase_time, "%H:%M")
    except ValueError:
        return False, "purchaseTime", "Invalid purchase time"

    # Validate items
    items = receipt_data.get("items")
    if not items or len(items) < 1:
        return False, "items", "No items or less than one item"

    # Validate each item
    for index, item in enumerate(items):
        short_description = item.get("shortDescription")
        if not short_description or not re.match("^[\\w\\s\\-]+$", short_description):
            return False, f"items[{index}].shortDescription", "Invalid short description"

        price = item.get("price")
        if not price or not re.match(r"^\d+\.\d{2}$", price):
            return False, f"items[{index}].price", "Invalid price format"

    # Validate total
    total = receipt_data.get("total")
    try:
        float_total = float(total)
        if float_total < 0:
            raise ValueError
    except (ValueError, TypeError):
        return False, "total", "Invalid total amount"

    # All validations passed
    return True, None, "Valid receipt data"
if __name__ == '__main__':
    app.run(debug=True)