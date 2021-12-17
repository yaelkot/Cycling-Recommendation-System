from flask import Flask
from flask import jsonify
from flask import request
from src.backend.mybackend import Database

app = Flask(__name__)
db = Database('BikeShare.csv')


@app.route('/', methods=["GET"])
def get_recommendations():
    start_station = request.args.get('startlocation')
    duration = request.args.get('timeduration')
    k = request.args.get('k')
    if duration is None or start_station is None or k is None:
        return jsonify('one argument or more is missing'), 400
    res = db.get_places(start_station=start_station, time_duration=duration, k=k)
    if len(res) == 0:
        return jsonify('Start Station does not exist'), 404
    return jsonify(res)


if __name__ == "__main__":
    app.run()
