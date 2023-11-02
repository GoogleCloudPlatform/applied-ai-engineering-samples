"""Expose REST API for product cataloging functionality."""
import os

from flask import Flask
from flask_restful import Resource, Api, reqparse

import category, config

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('description')
parser.add_argument('image')

class Category(Resource):
    def post(self):
        """Return ranking of suggested categories.

        Args:
            description:
            image: base64 encoded string
        Returns:
            list of categories
        """
        args = parser.parse_args()
        description = args['description']
        image = args['image']
        res = category.retrieve_and_rank(description, image, base64=True)
        return res

api.add_resource(Category, '/v1/categories')

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=True, port=server_port, host='0.0.0.0')
