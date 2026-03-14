from flask import Flask, request, redirect, url_for, render_template
from decimal import Decimal, InvalidOperation

from database import db, init
from currency import get_nbp_rate

app = Flask(__name__)
init()


def parse_decimal(value):
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError):
        return Decimal("0.00")


@app.route("/")
def index():
    conn = db()
    c = conn.cursor()
    c.execute("""
        SELECT id, date, distance, currency, 
        COALESCE(fuel_cost_PLN, '0.00'), 
        COALESCE(accommodation_cost_PLN, '0.00'), 
        COALESCE(diet_cost_PLN, '0.00'), 
        COALESCE(fuel_cost, '0.00'), 
        COALESCE(accommodation_cost, '0.00'), 
        COALESCE(diet_cost, '0.00')
        FROM trips
        WHERE deleted = 0
        ORDER BY date DESC, id DESC
    """)
    trips = c.fetchall()
    conn.close()
    return render_template("index.html", trips=trips)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        date = request.form["date"]
        distance = int(request.form["distance"])
        currency = request.form["currency"]

        fuel_cost = parse_decimal(request.form["fuel_cost"])
        accommodation_cost = parse_decimal(request.form.get("accommodation_cost"))
        diet_cost = parse_decimal(request.form.get("diet_cost"))

        rate = get_nbp_rate(currency, date)

        fuel_cost_pln = (fuel_cost * rate).quantize(Decimal("0.01"))
        accommodation_cost_pln = (accommodation_cost * rate).quantize(Decimal("0.01"))
        diet_cost_pln = (diet_cost * rate).quantize(Decimal("0.01"))

        conn = db()
        c = conn.cursor()
        c.execute("""
            INSERT INTO trips
            (date, distance, currency, fuel_cost_PLN, accommodation_cost_PLN, diet_cost_PLN,
             fuel_cost, accommodation_cost, diet_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date, distance, currency, str(fuel_cost_pln), str(accommodation_cost_pln),
            str(diet_cost_pln), str(fuel_cost), str(accommodation_cost), str(diet_cost)
        ))
        conn.commit()
        conn.close()
        return redirect(url_for("report"))
    return render_template("form.html")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = db()
    c = conn.cursor()
    c.execute("SELECT * FROM trips WHERE id=? AND deleted=0", (id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return redirect(url_for("index"))

    if request.method == "POST":
        date = request.form["date"]
        distance = int(request.form["distance"])
        currency = request.form["currency"]

        fuel_cost = parse_decimal(request.form["fuel_cost"])
        accommodation_cost = parse_decimal(request.form.get("accommodation_cost"))
        diet_cost = parse_decimal(request.form.get("diet_cost"))

        rate = get_nbp_rate(currency, date)

        fuel_cost_pln = (fuel_cost * rate).quantize(Decimal("0.01"))
        accommodation_cost_pln = (accommodation_cost * rate).quantize(Decimal("0.01"))
        diet_cost_pln = (diet_cost * rate).quantize(Decimal("0.01"))

        c.execute("""
            UPDATE trips
            SET date=?, distance=?, currency=?, 
                fuel_cost_PLN=?, accommodation_cost_PLN=?, diet_cost_PLN=?,
                fuel_cost=?, accommodation_cost=?, diet_cost=?
            WHERE id=?
        """, (
            date, distance, currency, str(fuel_cost_pln), str(accommodation_cost_pln),
            str(diet_cost_pln), str(fuel_cost), str(accommodation_cost), str(diet_cost), id
        ))
        conn.commit()
        conn.close()
        return redirect(url_for("report"))

    trip = {
        "date": row[1],
        "distance": row[2],
        "currency": row[3],
        "fuel_cost": row[7],
        "accommodation_cost": row[8],
        "diet_cost": row[9]
    }
    conn.close()
    return render_template("form.html", trip=trip)


@app.route("/delete/<int:id>")
def delete(id):
    conn = db()
    c = conn.cursor()
    c.execute("UPDATE trips SET deleted=1 WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/report")
def report():
    conn = db()
    c = conn.cursor()
    c.execute("""
        SELECT id, date, currency, 
        COALESCE(fuel_cost_PLN, '0.00'), 
        COALESCE(accommodation_cost_PLN, '0.00'), 
        COALESCE(diet_cost_PLN, '0.00'),
        COALESCE(fuel_cost, '0.00'), 
        COALESCE(accommodation_cost, '0.00'), 
        COALESCE(diet_cost, '0.00')
        FROM trips
        WHERE deleted=0
        ORDER BY date DESC, id DESC
    """)
    trips = c.fetchall()
    conn.close()
    total = Decimal("0.00")
    for i in trips:
        fuel = parse_decimal(i[3])
        accom = parse_decimal(i[4])
        diet = parse_decimal(i[5])
        total += (fuel + accom + diet).quantize(Decimal("0.01"))
    return render_template("report.html", trips=trips, total=total)


if __name__ == "__main__":
    app.run(debug=True)
