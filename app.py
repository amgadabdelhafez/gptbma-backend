from flask import Flask, jsonify, request
from flask_cors import CORS
from db_utils import db, init_db, RateCard, BillingData, to_dict

# Initialize Flask app
app = Flask(__name__)

CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gptbma.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database using the utility function from db_utils.py
init_db(app)

# CRUD operations for rate_card
@app.route('/api/rate_card', methods=['POST', 'GET', 'PUT', 'DELETE'])
def manage_rate_card():
    rate_card_fields = ['sku_id','service_category','service_name','service_offering','offering_unit','pricing_unit','pricing_quantity','unit_price']
    if request.method == 'POST':
        data = request.json
        # if data is an array of objects, iterate through each object and create a new entry in the database for each object
        if isinstance(data, list):
            for obj in data:
                new_entry = RateCard(sku_id=obj['sku_id'], service_category=obj['service_category'], service_name=obj['service_name'], service_offering=obj['service_offering'], offering_unit=obj['offering_unit'], pricing_unit=obj['pricing_unit'], pricing_quantity=obj['pricing_quantity'], unit_price=obj['unit_price'])
                db.session.add(new_entry)
            db.session.commit()
            return jsonify({"message": "Created"}), 201
        else:
            new_entry = RateCard(sku_id=data['sku_id'], service_category=data['service_category'], service_name=data['service_name'], service_offering=data['service_offering'], offering_unit=data['offering_unit'], pricing_unit=data['pricing_unit'], pricing_quantity=data['pricing_quantity'], unit_price=data['unit_price'])
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"message": "Created"}), 201
    elif request.method == 'GET':
        sku_id = request.args.get('sku_id')
        service_offering = request.args.get('service_offering')
        if sku_id:
            entry = RateCard.query.get(sku_id)
            if entry:
                return jsonify(to_dict(entry, rate_card_fields)), 200
            return jsonify({"message": "Not found"}), 404

        if service_offering:
            entries = RateCard.query.filter_by(service_offering=service_offering).all()
            if entries:
                return jsonify([to_dict(e, rate_card_fields) for e in entries]), 200
            return jsonify({"message": "Not found"}), 404

        entries = RateCard.query.all()
        return jsonify([to_dict(e, rate_card_fields) for e in entries]), 200
    elif request.method == 'PUT':
        data = request.json
        entry = RateCard.query.get(data['sku_id'])
        if entry:
            entry.sku_id = data['sku_id']
            entry.service_category = data['service_category']
            entry.service_name = data['service_name']
            entry.service_offering = data['service_offering']
            entry.offering_unit = data['offering_unit']
            entry.pricing_unit = data['pricing_unit']
            entry.pricing_quantity = data['pricing_quantity']
            entry.unit_price = data['unit_price']
            db.session.commit()
            return jsonify({"message": "Updated"}), 200
        return jsonify({"message": "Not found"}), 404
    elif request.method == 'DELETE':
        data = request.json
        entry = RateCard.query.get(data['sku_id'])
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return jsonify({"message": "Deleted"}), 200
        return jsonify({"message": "Not found"}), 404
    return jsonify({"message": "Operation not supported"}), 400

# CRUD operations for billing_data
@app.route('/api/billing_data', methods=['POST', 'GET', 'PUT', 'DELETE'])
def manage_billing_data():
    billing_data_fields = ['charge_id', 'sku_id', 'service_offering', 'billing_period_start', 'billing_period_end', 'resource_name', 'resource_type', 'usage_unit', 'usage_quantity']
    if request.method == 'POST':
        data = request.json
        new_entry = BillingData(charge_id=data['charge_id'], sku_id=data['sku_id'], service_offering=data['service_offering'], billing_period_start=data['billing_period_start'], billing_period_end=data['billing_period_end'], resource_name=data['resource_name'], resource_type=data['resource_type'], usage_unit=data['usage_unit'], usage_quantity=data['usage_quantity'], effective_cost=data['effective_cost'])
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"message": "Created"}), 201
    elif request.method == 'GET':
        id = request.args.get('charge_id')
        resource_name = request.args.get('resource_name')

        if id:
            entry = BillingData.query.get(id)
            if entry:
                return jsonify(to_dict(entry, billing_data_fields)), 200
            return jsonify({"message": "Not found"}), 404

        if resource_name:
            entries = BillingData.query.filter_by(resource_name=resource_name).all()
            if entries:
                return jsonify([to_dict(e, billing_data_fields) for e in entries]), 200
            return jsonify({"message": "Not found"}), 404

        entries = BillingData.query.all()
        return jsonify([to_dict(e, billing_data_fields) for e in entries]), 200

    elif request.method == 'PUT':
        data = request.json
        entry = BillingData.query.get(data['charge_id'])
        if entry:
            entry.charge_id = data['charge_id']
            entry.sku_id = data['sku_id']
            entry.service_offering = data['service_offering']
            entry.billing_period_start = data['billing_period_start']
            entry.billing_period_end = data['billing_period_end']
            entry.resource_name = data['resource_name']
            entry.resource_type = data['resource_type']
            entry.usage_unit = data['usage_unit']
            entry.usage_quantity = data['usage_quantity']
            db.session.commit()
            return jsonify({"message": "Updated"}), 200
        return jsonify({"message": "Not found"}), 404
    elif request.method == 'DELETE':
        data = request.json
        entry = BillingData.query.get(data['id'])
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return jsonify({"message": "Deleted"}), 200
        return jsonify({"message": "Not found"}), 404
    return jsonify({"message": "Operation not supported"}), 400


# Calculate resource estimate
@app.route('/api/calculate_estimate', methods=['POST'])
def calculate_estimate():
    # sample payload: {"usage_data": {"sku001": 8, "sku002": 32}}
    data = request.json
    unit_prices_by_sku_ids = {e.sku_id: e.unit_price for e in RateCard.query.all()}
    usage_data = data['usage_data']
    estimates = {}
    for sku_id, usage in usage_data.items():
        if sku_id in unit_prices_by_sku_ids:
            unit_price = unit_prices_by_sku_ids[sku_id]
            estimates[sku_id] = usage * unit_price
    return jsonify({"estimates": estimates}), 200

# Get cost estimate of a resource
@app.route('/api/get_resource_estimate', methods=['GET'])
def resource_estimate():
    # sample payload {"resource_name": "app_1_vm_1"}
    resource_name = request.args.get('resource_name')
    if resource_name:
        entries = BillingData.query.filter_by(resource_name=resource_name).all()
        resource_estimate = sum([entry.effective_cost for entry in entries])
        return jsonify({"resource_estimate": resource_estimate}), 200
    return jsonify({"message": "resource name not provided"}), 400

# Get all resources and their estimates
@app.route('/api/all_resource_estimates', methods=['GET'])
def all_resource_estimates():
    # sample payload {"resource_name": "app_1_vm_1"}
    # sample response: {"resource_estimates": {"app_1_vm_1": 100, "app_1_vm_1": 200}}
    apps = db.session.query(BillingData.resource_name).distinct()
    resource_estimates = {}
    for app in apps:
        entries = BillingData.query.filter_by(resource_name=app.resource_name).all()
        total_cost = sum([entry.effective_cost for entry in entries if entry.effective_cost is not None])
        resource_estimates[app.resource_name] = total_cost
    return jsonify(resource_estimates), 200

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
