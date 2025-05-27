const WebSocket = require('ws');
const OSRM = require('osrm');
const osrm = new OSRM('/path/to/osm-data.osrm'); // Adjust path to your OSRM data

const wss = new WebSocket.Server({ port: 8080 });
const waitingUsers = new Map(); // Map to store WebSocket clients and their data

console.log('Server running on ws://localhost:8080');

wss.on('connection', function connection(ws) {
    ws.on('message', function incoming(message) {
        const userData = JSON.parse(message);
        waitingUsers.set(ws, userData);

        while (waitingUsers.size >= 3) {
            const group = findBestGroup([...waitingUsers.entries()]);
            if (group) {
                const groupData = processGroup(group);
                group.forEach(([ws]) => {
                    ws.send(JSON.stringify({ type: 'group', ...groupData }));
                    waitingUsers.delete(ws);
                });
            } else {
                break;
            }
        }

        if (waitingUsers.has(ws)) {
            ws.send(JSON.stringify({ type: 'wait' }));
        }
    });

    ws.on('close', () => waitingUsers.delete(ws));
});

function findBestGroup(users) {
    let bestGroup = null;
    let minSum = Infinity;

    for (let i = 0; i < users.length - 2; i++) {
        for (let j = i + 1; j < users.length - 1; j++) {
            for (let k = j + 1; k < users.length; k++) {
                const triplet = [users[i], users[j], users[k]];
                const sum = calculateTripletDistance(triplet.map(([, data]) => data.origin));
                if (sum < minSum) {
                    minSum = sum;
                    bestGroup = triplet;
                }
            }
        }
    }
    return bestGroup;
}

function calculateTripletDistance(origins) {
    let sum = 0;
    for (let i = 0; i < origins.length; i++) {
        for (let j = i + 1; j < origins.length; j++) {
            sum += getDistance(origins[i], origins[j]);
        }
    }
    return sum;
}

function getDistance(point1, point2) {
    // Synchronous approximation for simplicity; in practice, use osrm.route asynchronously
    return new Promise((resolve) => {
        osrm.route({
            coordinates: [point1, point2],
            overview: 'false'
        }, (err, result) => {
            if (err) resolve(100000); // Fallback distance on error
            else resolve(result.routes[0].distance);
        });
    }).then(distance => distance);
}

function processGroup(group) {
    const origins = group.map(([, data]) => data.origin);
    const destinations = group.map(([, data]) => data.destination);

    const groupOrigin = calculateSharedPoint(origins);
    const groupDestination = calculateSharedPoint(destinations);

    return {
        groupOrigin,
        groupDestination,
        companions: origins
    };
}

function calculateSharedPoint(points) {
    let minSum = Infinity;
    let bestPoint = null;

    points.forEach(point => {
        let sum = 0;
        points.forEach(other => {
            if (point !== other) {
                sum += getDistance(point, other);
            }
        });
        if (sum < minSum) {
            minSum = sum;
            bestPoint = point;
        }
    });
    return bestPoint;
}