from flask import Flask, Blueprint, request, jsonify
from flasgger import Swagger
from flasgger import swag_from

app = Flask(__name__)
Swagger(app)

@app.route('/')
def index():
    return {"message": "Documentation is available at /apidocs"}

trips = []

bp = Blueprint("api", __name__)

def _get_next_id():
    if not trips:
        return 1
    return max(t["id"] for t in trips) + 1


@bp.route("/trips", methods=["GET"])
def get_trips():
    """
    Получить список всех туристических поездок
    ---
    parameters:
      - name: sort
        in: query
        type: string
        required: false
        description: Поле для сортировки (destination, days, price, hotel, rating)
      - name: order
        in: query
        type: string
        required: false
        description: "Порядок сортировки: asc или desc"
    responses:
      200:
        description: Список поездок
        schema:
          type: array
          items:
            type: object
            properties:
              id: {type: integer}
              destination: {type: string}
              days: {type: integer}
              price: {type: number}
              hotel: {type: string}
              rating: {type: number}
    """
    sort = request.args.get("sort")
    order = request.args.get("order", "asc").lower()

    data = list(trips)
    if sort and len(data) > 0 and sort in data[0]:
        data.sort(key=lambda x: x.get(sort), reverse=(order == "desc"))

    return jsonify(data)


@bp.route("/trips/<int:trip_id>", methods=["GET"])
def get_trip(trip_id):
    """
    Получить поездку по ID
    ---
    parameters:
      - name: trip_id
        in: path
        type: integer
        required: true
        description: ID поездки
    responses:
      200:
        description: Данные поездки
        schema:
          type: object
          properties:
            id: {type: integer}
            destination: {type: string}
            days: {type: integer}
            price: {type: number}
            hotel: {type: string}
            rating: {type: number}
      404:
        description: Поездка не найдена
    """
    trip = next((t for t in trips if t["id"] == trip_id), None)
    if not trip:
        return jsonify({"error": "Поездка не найдена"}), 404
    return jsonify(trip)


@bp.route("/trips", methods=["POST"])
def create_trip():
    """
    Добавить новую поездку
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - destination
            - days
            - price
            - hotel
            - rating
          properties:
            destination:
              type: string
            days:
              type: integer
            price:
              type: number
            hotel:
              type: string
            rating:
              type: number
    responses:
      201:
        description: Поездка добавлена
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Некорректный JSON"}), 400

    required = ["destination", "days", "price", "hotel", "rating"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Отсутствует поле: {field}"}), 400

    new_trip = {
        "id": _get_next_id(),
        "destination": data["destination"],
        "days": int(data["days"]),
        "price": float(data["price"]),
        "hotel": data["hotel"],
        "rating": float(data["rating"])
    }
    trips.append(new_trip)
    return jsonify(new_trip), 201


@bp.route("/trips/<int:trip_id>", methods=["PUT"])
def update_trip(trip_id):
    """
    Обновить данные поездки по ID
    ---
    parameters:
      - name: trip_id
        in: path
        type: integer
        required: true
        description: ID поездки для обновления
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            destination: {type: string}
            days: {type: integer}
            price: {type: number}
            hotel: {type: string}
            rating: {type: number}
    responses:
      200:
        description: Поездка успешно обновлена
      404:
        description: Поездка не найдена
    """
    data = request.get_json()
    trip = next((t for t in trips if t["id"] == trip_id), None)
    if not trip:
        return jsonify({"error": "Поездка не найдена"}), 404

    for field in ["destination", "days", "price", "hotel", "rating"]:
        if field in data:
            trip[field] = data[field]
    return jsonify(trip)


@bp.route("/trips/<int:trip_id>", methods=["DELETE"])
def delete_trip(trip_id):
    """
    Удалить поездку по ID
    ---
    parameters:
      - name: trip_id
        in: path
        type: integer
        required: true
        description: ID поездки для удаления
    responses:
      200:
        description: Успешное удаление
        schema:
          type: object
          properties:
            message: {type: string}
      404:
        description: Поездка не найдена
    """
    global trips
    before = len(trips)
    trips = [t for t in trips if t["id"] != trip_id]
    if len(trips) == before:
        return jsonify({"error": "Поездка не найдена"}), 404
    return jsonify({"message": "Поездка удалена"})


@bp.route("/trips/stats", methods=["GET"])
def trips_stats():
    """
    Получить статистику по числовым полям
    ---
    responses:
      200:
        description: Среднее, минимальное и максимальное значения по числовым полям
        schema:
          type: object
          properties:
            days:
              type: object
              properties:
                min: {type: integer}
                max: {type: integer}
                avg: {type: number}
            price:
              type: object
              properties:
                min: {type: number}
                max: {type: number}
                avg: {type: number}
            rating:
              type: object
              properties:
                min: {type: number}
                max: {type: number}
                avg: {type: number}
      400:
        description: Нет данных
    """
    if not trips:
        return jsonify({"error": "Нет данных"}), 400

    days = [t["days"] for t in trips]
    price = [t["price"] for t in trips]
    rating = [t["rating"] for t in trips]

    stats = {
        "days": {"min": min(days), "max": max(days), "avg": round(sum(days) / len(days), 2)},
        "price": {"min": min(price), "max": max(price), "avg": round(sum(price) / len(price), 2)},
        "rating": {"min": min(rating), "max": max(rating), "avg": round(sum(rating) / len(rating), 2)}
    }

    return jsonify(stats)


app.register_blueprint(bp, url_prefix="/api")

if __name__ == "__main__":
    app.run(debug=True)
