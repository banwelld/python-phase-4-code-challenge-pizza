#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


class AllRestaurants(Resource):

    def get(self):
        restaurants = [
            r.to_dict(rules=("-restaurant_pizzas",)) for r in Restaurant.query.all()
        ]
        return make_response(restaurants, 200)


class RestaurantByID(Resource):

    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()

        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)

        return make_response(restaurant.to_dict(), 200)

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()

        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)

        db.session.delete(restaurant)
        db.session.commit()

        return make_response({}, 204)


class AllPizzas(Resource):

    def get(self):
        pizzas = [p.to_dict(rules=("-restaurant_pizzas",)) for p in Pizza.query.all()]
        return make_response(pizzas, 200)


class AllRestaurantPizzas(Resource):

    def post(self):
        try:
            restaurant = Restaurant.query.filter_by(
                id=request.json.get("restaurant_id")
            ).first()
            pizza = Pizza.query.filter_by(id=request.json.get("pizza_id")).first()

            if not all((restaurant, pizza)):
                raise ValueError("One or both ID values is null or invalid")

            restaurant_pizza = RestaurantPizza(
                restaurant=restaurant, pizza=pizza, price=request.json.get("price")
            )
            db.session.add(restaurant_pizza)
            db.session.commit()

            return make_response(restaurant_pizza.to_dict(), 201)

        except Exception:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(AllRestaurants, "/restaurants")
api.add_resource(RestaurantByID, "/restaurants/<int:id>")
api.add_resource(AllPizzas, "/pizzas")
api.add_resource(AllRestaurantPizzas, "/restaurant_pizzas")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
