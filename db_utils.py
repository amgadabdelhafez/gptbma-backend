from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Define RateCard model
class RateCard(db.Model):
    sku_id = db.Column(db.String(50), primary_key=True)
    service_category = db.Column(db.String(50), nullable=False)
    service_name = db.Column(db.String(50), nullable=False)
    service_offering = db.Column(db.String(50), nullable=False)
    offering_unit = db.Column(db.String(50), nullable=False)
    pricing_unit = db.Column(db.String(50), nullable=False)
    pricing_quantity = db.Column(db.Float, nullable=False)

    unit_price = db.Column(db.Float, nullable=False) 

# Define BillingData model
class BillingData(db.Model):
    charge_id = db.Column(db.String(50), primary_key=True)
    sku_id = db.Column(db.String(50), db.ForeignKey('rate_card.sku_id'), nullable=False)
    service_offering = db.Column(db.String(50), nullable=False)

    billing_period_start = db.Column(db.String(50), nullable=False)
    billing_period_end = db.Column(db.String(50), nullable=False)

    resource_name = db.Column(db.String(50), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
 
    usage_unit = db.Column(db.String(50), nullable=False)
    usage_quantity = db.Column(db.Float, nullable=False)

    effective_cost = db.Column(db.Float, nullable=True)

def init_db(app):
    with app.app_context():
        db.init_app(app)
        db.create_all()
        services = []
        charges = []
        # Check if the rate cards table is empty and initiate the data if it is
        if RateCard.query.count() == 0:
            services = [
            {
                'sku_id': 'sku001',
                'service_category': 'compute',
                'service_name': 'virtual machine',
                'service_offering': 'cpu',
                'offering_unit': 'vcpu',
                'pricing_unit': 'hour',
                'pricing_quantity': 1,
                'unit_price': 0.23,
            },
            {
                'sku_id': 'sku002',
                'service_category': 'compute',
                'service_name': 'virtual machine',
                'service_offering': 'memory',
                'offering_unit': 'gb',
                'pricing_unit': 'hour',
                'pricing_quantity': 1,
                'unit_price': 0.03,
            },
            {
                'sku_id': 'sku003',
                'service_category': 'compute',
                'service_name': 'bare metal',
                'service_offering': 'cpu',
                'offering_unit': 'vcpu',
                'pricing_unit': 'hour',
                'pricing_quantity': 1,
                'unit_price': 0.02,
            },
            {
                'sku_id': 'sku004',
                'service_category': 'compute',
                'service_name': 'bare metal',
                'service_offering': 'memory',
                'offering_unit': 'gb',
                'pricing_unit': 'hour',
                'pricing_quantity': 1,
                'unit_price': 0.13,
            },
            {
                'sku_id': 'sku005',
                'service_category': 'compute',
                'service_name': 'container',
                'service_offering': 'cpu',
                'offering_unit': 'vcpu',
                'pricing_unit': 'hour',
                'pricing_quantity': 1,
                'unit_price': 0.23,
            },
            {
                'sku_id': 'sku006',
                'service_category': 'compute',
                'service_name': 'container',
                'service_offering': 'memory',
                'offering_unit': 'gb',
                'pricing_unit': 'hour',
                'pricing_quantity': 1,
                'unit_price': 0.02,
            },
            {
                'sku_id': 'sku007',
                'service_category': 'observability',
                'service_name': 'logs',
                'service_offering': 'type_1',
                'offering_unit': 'gb',
                'pricing_unit': 'day',
                'pricing_quantity': 1,
                'unit_price': 0.30,
            },
            {
                'sku_id': 'sku008',
                'service_category': 'observability',
                'service_name': 'logs',
                'service_offering': 'type_2',
                'offering_unit': 'gb',
                'pricing_unit': 'day',
                'pricing_quantity': 1,
                'unit_price': 0.43,
            },
            {
                'sku_id': 'sku009',
                'service_category': 'observability',
                'service_name': 'traces',
                'service_offering': 'type_1',
                'offering_unit': 'mts',
                'pricing_unit': 'day',
                'pricing_quantity': 10000,
                'unit_price': 0.33,
            },
            {
                'sku_id': 'sku010',
                'service_category': 'observability',
                'service_name': 'metrics',
                'service_offering': 'type_1',
                'offering_unit': 'mts',
                'pricing_unit': 'day',
                'pricing_quantity': 1000000,
                'unit_price': 0.33,
            },
            ]

        if BillingData.query.count() == 0:
            charges = [
            {
                'charge_id': 'charge001',
                'resource_name': 'app_1_vm_1',
                'resource_type': 'app_vm',
                'sku_id': 'sku001',
                'service_offering': 'cpu',
                'billing_period_start': '20231201',
                'billing_period_end': '20231231',
                'usage_unit': 'vcpu',
                'usage_quantity': 8,
                'effective_cost': 560.34,
            },
            {
                'charge_id': 'charge002',
                'resource_name': 'app_1_vm_1',
                'resource_type': 'app_vm',
                'sku_id': 'sku002',
                'service_offering': 'memory',
                'billing_period_start': '20231201',
                'billing_period_end': '20231231',
                'usage_unit': 'gb',
                'usage_quantity': 64,
                'effective_cost': 230.34,
            },
            {
                'charge_id': 'charge003',
                'resource_name': 'app_1_logs',
                'resource_type': 'app_logs',
                'sku_id': 'sku007',
                'service_offering': 'logs',
                'billing_period_start': '20231201',
                'billing_period_end': '20231231',
                'usage_unit': 'gb',
                'usage_quantity': 128000,
                'effective_cost': 1560.34,
            },
            {
                'charge_id': 'charge004',
                'resource_name': 'app_1_metrics',
                'resource_type': 'app_metrics',
                'sku_id': 'sku008',
                'service_offering': 'metrics',
                'billing_period_start': '20231201',
                'billing_period_end': '20231231',
                'usage_unit': 'mts',
                'usage_quantity': 802393,
                'effective_cost': 5560.34,
            }            
            ]

        for service in services:
            new_entry = RateCard(**service)
            db.session.add(new_entry)

        for charge in charges:
            new_entry = BillingData(**charge)
            db.session.add(new_entry)

        db.session.commit()

def to_dict(model_instance, fields_to_include):
    return {field: getattr(model_instance, field) for field in fields_to_include}