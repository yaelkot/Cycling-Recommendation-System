from flask import Flask
from flask import jsonify
from flask import request
from mybackend import Database

app = Flask(__name__)
db = Database('BikeShare.csv')


@app.route('/', methods=["GET"])
def get_recommendations():
    start_station = request.args.get('startlocation')
    duration = request.args.get('timeduration')
    k = request.args.get('k')
    res = db.get_places(start_station=start_station,time_duration=duration, k=k)
    return jsonify(res)


if __name__ == "__main__":
    app.run()
