# app.py

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'replace-with-your-own-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory storage of applied users:
# {
#   user_id_str: {
#       "origin": (lat, lng),
#       "destination": (lat, lng),
#       "gender": "male"/"female"/etc,
#       "rate": float,
#       "sid": socket session id  # so we can emit back to them
#   },
#   ...
# }
applied_users = {}

# Maximum “nearby” radius in decimal degrees (~around ~2km)
NEARBY_RADIUS = 0.02


@app.route('/user/<user_id>')
def user_page(user_id):
    """
    Serves the single HTML template for each user_id. The client JS
    will extract user_id, and on first connection also randomly
    assign “gender” and “rate” to this user.
    """
    return render_template('user.html', user_id=user_id)


@socketio.on('connect')
def handle_connect():
    # Nothing special on connect; the client will send an "apply" event later.
    pass


@socketio.on('disconnect')
def handle_disconnect():
    # If a user disconnects before applying or after, remove them from applied_users:
    to_remove = None
    for uid, info in applied_users.items():
        if info.get('sid') == request.sid:
            to_remove = uid
            break
    if to_remove:
        del applied_users[to_remove]


@socketio.on('apply')
def handle_apply(data):
    """
    Received when a user clicks “Apply” with their origin/destination.
    data = {
        "user_id": "1",
        "origin": [lat, lng],
        "destination": [lat, lng],
        "gender": "female",
        "rate": 4.2
    }
    """
    user_id = data.get('user_id')
    origin = tuple(data.get('origin'))      # (lat, lng)
    destination = tuple(data.get('destination'))
    gender = data.get('gender')
    rate = data.get('rate')

    # Store (or overwrite) in applied_users
    applied_users[user_id] = {
        'origin': origin,
        'destination': destination,
        'gender': gender,
        'rate': rate,
        'sid': request.sid
    }

    # Immediately compute “nearby” users for this one:
    near_list = []
    for other_id, info in applied_users.items():
        if other_id == user_id:
            continue
        o_lat, o_lng = info['origin']
        u_lat, u_lng = origin
        if (abs(o_lat - u_lat) <= NEARBY_RADIUS) and (abs(o_lng - u_lng) <= NEARBY_RADIUS):
            # within bounding box; you could also compute full haversine if desired
            near_list.append({
                'user_id': other_id,
                'origin': info['origin'],
                'gender': info['gender'],
                'rate': info['rate']
            })

    # Emit back to this user only:
    emit('near_users', {'near_users': near_list})

    # If total applied_users count == 3, compute central origin/destination
    if len(applied_users) == 3:
        # Gather all origins and destinations
        origins = [info['origin'] for info in applied_users.values()]
        destinations = [info['destination'] for info in applied_users.values()]

        # Compute simple average of latitudes and longitudes
        avg_orig_lat = sum(o[0] for o in origins) / 3.0
        avg_orig_lng = sum(o[1] for o in origins) / 3.0
        avg_dest_lat = sum(d[0] for d in destinations) / 3.0
        avg_dest_lng = sum(d[1] for d in destinations) / 3.0

        station_payload = {
            'origin': [avg_orig_lat, avg_orig_lng],
            'destination': [avg_dest_lat, avg_dest_lng]
        }

        # Emit to all three clients:
        for info in applied_users.values():
            sid = info['sid']
            socketio.emit('station', station_payload, room=sid)


if __name__ == '__main__':
    # Use eventlet or gevent for production; for testing, debug=True is fine
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
