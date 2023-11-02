"""Exposes REST API for product cataloging functionality."""
import os

from flask import Flask
from flask_restful import Resource, Api

import category, config

app = Flask(__name__)
api = Api(app)

class Category(Resource):
    def get(self):
        return category.join_categories([config.TEST_PRODUCT_ID])

api.add_resource(Category, '/')
if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=True, port=server_port, host='0.0.0.0')
