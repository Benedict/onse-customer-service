from flask import jsonify, Blueprint, current_app, request
from schema import Schema, SchemaError, And

from customer_service.model import commands
from customer_service.model.customer import Customer
from customer_service.model.errors import CustomerNotFound

customers = Blueprint('customers', __name__, url_prefix='/customers/')

CREATE_PAYLOAD_SCHEMA = Schema({"firstName": And(str, len),
                                "surname": And(str, len)})


@customers.route('/<string:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer_repository = current_app.customer_repository

    customer = commands.get_customer(
        customer_id=int(customer_id),
        customer_repository=customer_repository)

    return jsonify(customerId=str(customer.customer_id),
                   firstName=customer.first_name,
                   surname=customer.surname)


@customers.route('/', methods=['POST'])
def create_customer():
    customer_repository = current_app.customer_repository

    if not request.is_json:
        raise ContentTypeError()

    body = request.get_json()

    CREATE_PAYLOAD_SCHEMA.validate(body)

    customer = Customer(first_name=body['firstName'],
                        surname=body['surname'])

    commands.create_customer(
        customer=customer,
        customer_repository=customer_repository)

    return jsonify(customerId=customer.customer_id,
                   firstName=customer.first_name,
                   surname=customer.surname), 201


@customers.errorhandler(CustomerNotFound)
def customer_not_found(e):
    return jsonify({
        'message': 'Customer not found'
    }), 404


@customers.errorhandler(SchemaError)
def invalid_schema(e):
    return jsonify({
        'message': str(e)
    }), 400


class ContentTypeError(RuntimeError):
    pass


@customers.errorhandler(ContentTypeError)
def content_type_error(e):
    return jsonify({
        'message': 'Request must be application/json'
    }), 400
