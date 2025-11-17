from flask import Flask, render_template, request, redirect
import firebase_admin
from firebase_admin import credentials, firestore
from flask import jsonify

app = Flask(__name__)

# ================================
# Firebase Setup
# ================================
cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# ================================
# HOME
# ================================
@app.route('/')
def index():
    return render_template('index.html')

# ================================
# DATACENTERS
# ================================
@app.route('/datacenters')
def datacenters():
    docs = db.collection("datacenters").stream()
    data = [(doc.id, doc.to_dict()['name'], doc.to_dict()['location']) for doc in docs]
    return render_template('datacenters.html', data=data)

@app.route('/add_datacenter', methods=['POST'])
def add_datacenter():
    name = request.form['name']
    location = request.form['location']
    db.collection("datacenters").add({"name": name, "location": location})
    return redirect('/datacenters')

@app.route('/datacenters/delete/<id>')
def delete_datacenter(id):
    db.collection("datacenters").document(id).delete()
    return redirect('/datacenters')

@app.route('/api/add_datacenter', methods=['POST'])
def api_add_datacenter():
    data = request.json
    name = data.get('name')
    location = data.get('location')
    
    doc_ref = db.collection("datacenters").add({"name": name, "location": location})
    
    return jsonify({"status": "success", "id": doc_ref[1].id, "name": name, "location": location})


# ================================
# RACKS
# ================================
@app.route('/racks')
def racks():
    racks_docs = db.collection("racks").stream()
    racks_data = []
    for r in racks_docs:
        r_data = r.to_dict()
        # Fetch datacenter name
        dc_doc = db.collection("datacenters").document(r_data['datacenter_id']).get()
        dc_name = dc_doc.to_dict()['name'] if dc_doc.exists else "Deleted DC"
        racks_data.append((r.id, r_data['rack_name'], r_data['capacity'], dc_name))

    # For the Add Rack form
    dc_docs = db.collection("datacenters").stream()
    datacenters = [(dc.id, dc.to_dict()['name'], dc.to_dict()['location']) for dc in dc_docs]

    return render_template('racks.html', data=racks_data, datacenters=datacenters)

@app.route('/add_rack', methods=['POST'])
def add_rack():
    rack_name = request.form['rack_name']
    capacity = request.form['capacity']
    datacenter_id = request.form['datacenter_id']
    db.collection("racks").add({"rack_name": rack_name, "capacity": capacity, "datacenter_id": datacenter_id})
    return redirect('/racks')

@app.route('/racks/delete/<id>')
def delete_rack(id):
    db.collection("racks").document(id).delete()
    return redirect('/racks')

@app.route('/api/add_rack', methods=['POST'])
def api_add_rack():
    data = request.json
    rack_name = data.get('rack_name')
    capacity = data.get('capacity')
    datacenter_id = data.get('datacenter_id')
    
    doc_ref = db.collection("racks").add({
        "rack_name": rack_name,
        "capacity": capacity,
        "datacenter_id": datacenter_id
    })
    
    return jsonify({
        "status": "success", 
        "id": doc_ref[1].id, 
        "rack_name": rack_name, 
        "capacity": capacity, 
        "datacenter_id": datacenter_id
    })

# ================================
# SERVERS
# ================================
@app.route('/servers')
def servers():
    servers_docs = db.collection("servers").stream()
    servers_data = []
    for s in servers_docs:
        s_data = s.to_dict()
        # Fetch rack name
        rack_doc = db.collection("racks").document(s_data['rack_id']).get()
        rack_name = rack_doc.to_dict()['rack_name'] if rack_doc.exists else "Deleted Rack"
        servers_data.append((
            s.id,
            s_data['server_name'],
            s_data['cpu_usage'],
            s_data['temperature'],
            s_data['status'],
            rack_name,
            s_data['rack_id']
        ))

    racks_docs = db.collection("racks").stream()
    racks = [(r.id, r.to_dict()['rack_name']) for r in racks_docs]

    return render_template('servers.html', data=servers_data, racks=racks)

@app.route('/servers/add', methods=['GET', 'POST'])
def add_server():
    if request.method == 'POST':
        name = request.form['server_name']
        rack_id = request.form['rack_id']
        cpu = request.form['cpu_usage']
        temp = request.form['temperature']
        status = request.form['status']
        db.collection("servers").add({
            "server_name": name,
            "rack_id": rack_id,
            "cpu_usage": cpu,
            "temperature": temp,
            "status": status
        })
    # Whether GET or POST, redirect to servers page
    return redirect('/servers')

@app.route('/servers/delete/<id>')
def delete_server(id):
    db.collection("servers").document(id).delete()
    return redirect('/servers')

@app.route('/api/add_server', methods=['POST'])
def api_add_server():
    data = request.json
    name = data.get('server_name')
    rack_id = data.get('rack_id')
    cpu = data.get('cpu_usage')
    temp = data.get('temperature')
    status = data.get('status')
    
    doc_ref = db.collection("servers").add({
        "server_name": name,
        "rack_id": rack_id,
        "cpu_usage": cpu,
        "temperature": temp,
        "status": status
    })
    
    return jsonify({
        "status": "success",
        "id": doc_ref[1].id,
        "server_name": name,
        "rack_id": rack_id,
        "cpu_usage": cpu,
        "temperature": temp,
        "status": status
    })

# ================================
# RUN APP
# ================================
if __name__ == '__main__':
    app.run(debug=True)
