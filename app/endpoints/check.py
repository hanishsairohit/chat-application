from flask import Blueprint, jsonify, make_response

status_blueprint = Blueprint('check', __name__, url_prefix='/check')

@status_blueprint.route('', methods=['POST'])
def status():
    return make_response(jsonify({'health': 'ok'}), 200)
