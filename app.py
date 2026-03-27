from flask import Flask, render_template, request, redirect, url_for, session
import os
import heapq
from collections import deque

app = Flask(__name__, template_folder=os.path.join(os.getcwd(), "templates"))
app.secret_key = "secret123"

# ================= USERS =================
USERS = {
    "admin": {"username": "admin", "password": "admin123"},
    "ngo": {"username": "ngo", "password": "ngo123"},
    "user": {"username": "user", "password": "user123"}
}

# ================= NGO DATA =================
NGO_DATA = {
    "NGO1": {"location": "B", "capacity": 50},
    "NGO2": {"location": "C", "capacity": 30},
    "NGO3": {"location": "D", "capacity": 70}
}

# ================= GRAPH =================
graph = {
    "A": [("B", 5), ("C", 10)],
    "B": [("D", 3)],
    "C": [("D", 1)],
    "D": []
}

# ================= DIJKSTRA =================
def dijkstra(graph, start):
    pq = [(0, start)]
    distances = {node: float('inf') for node in graph}
    distances[start] = 0

    while pq:
        curr_dist, curr_node = heapq.heappop(pq)

        for neighbor, weight in graph[curr_node]:
            distance = curr_dist + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))

    return distances

# ================= BFS =================
def bfs_nearest(start):
    visited = set()
    queue = deque([start])

    while queue:
        node = queue.popleft()

        if node not in visited:
            visited.add(node)

            for name, info in NGO_DATA.items():
                if info["location"] == node:
                    return name

            for neighbor, _ in graph[node]:
                queue.append(neighbor)

    return None

# ================= GREEDY =================
def choose_best_ngo(start_location):
    distances = dijkstra(graph, start_location)

    best_ngo = None
    best_score = float('inf')

    for name, info in NGO_DATA.items():
        dist = distances[info["location"]]
        capacity = info["capacity"]

        score = dist - (capacity * 0.1)

        if score < best_score:
            best_score = score
            best_ngo = name

    return best_ngo

# ================= PRIORITY QUEUE =================
food_queue = []

def add_food_priority(food, qty):
    heapq.heappush(food_queue, (-qty, food))

# ================= BINARY SEARCH =================
def binary_search_ngos(sorted_list, target):
    low = 0
    high = len(sorted_list) - 1

    while low <= high:
        mid = (low + high) // 2

        if sorted_list[mid] == target:
            return sorted_list[mid]
        elif sorted_list[mid] < target:
            low = mid + 1
        else:
            high = mid - 1

    return None

# ================= HOME =================
@app.route('/')
def home():
    return render_template("index.html")

# ================= REGISTER =================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return redirect(url_for('login'))
    return render_template("register.html")

# ================= LOGIN =================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        username = request.form.get('username')
        password = request.form.get('password')

        user = USERS.get(role)

        if user and username == user["username"] and password == user["password"]:
            session['user'] = username
            session['role'] = role
            return redirect(url_for('dashboard'))
        else:
            return render_template("login.html", error="Invalid credentials ❌")

    return render_template("login.html")

# ================= DASHBOARD =================
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("dashboard.html", user=session['user'])

# ================= POST FOOD =================
@app.route('/post_food', methods=['GET', 'POST'])
def post_food():
    if 'user' not in session or session.get('role') != 'user':
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        food = request.form.get('food')
        qty = int(request.form.get('qty'))
        unit = request.form.get('unit')

        # 👇 USER SELECTED LOCATION
        user_location = request.form.get('location')

        # 👇 MAPPING (IMPORTANT FIX)
        location_map = {
            "clement town": "A",
            "subhash nagar": "B",
            "rajpur": "C",
            "prem nagar": "D",
            "ballupur": "A"
        }

        location = location_map.get(user_location, "A")

        # ================= DAA =================
        best_ngo = choose_best_ngo(location)   # Dijkstra + Greedy
        bfs_ngo = bfs_nearest(location)        # BFS
        add_food_priority(food, qty)           # Priority Queue

        ngo_names = sorted(NGO_DATA.keys())
        searched_ngo = binary_search_ngos(ngo_names, best_ngo)

        # ================= STORE =================
        session['food_data'] = [food, str(qty) + " " + unit, user_location]
        session['assigned_ngo'] = best_ngo
        session['bfs_ngo'] = bfs_ngo
        session['searched_ngo'] = searched_ngo

        return redirect(url_for('view_food'))

    return render_template("post_food.html")

# ================= VIEW FOOD =================
@app.route('/view_food')
def view_food():
    if 'user' not in session:
        return redirect(url_for('login'))

    data = session.get('food_data')
    ngo = session.get('assigned_ngo')
    bfs_ngo = session.get('bfs_ngo')
    searched_ngo = session.get('searched_ngo')

    return render_template("view_food.html", data=data, ngo=ngo, bfs_ngo=bfs_ngo, searched_ngo=searched_ngo)

# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)