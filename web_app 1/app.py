from flask import Flask
from flask import render_template, request, redirect
from flask import session
import sqlite3 as sql

app = Flask(__name__)
app.secret_key = "thanksgiving"


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/returnadmin")
def returnadmin():
    return render_template("adminlogin.html")


@app.route("/adminlogin", methods=["GET", "POST"])
def adminlogin():
    b = False
    if request.method == "POST":
        try:
            un = request.form['un']
            pas = request.form['pass']
            if not un or not pas:
                return redirect("/returnadmin")
            else:
                with sql.connect("database.db") as con:
                    cur = con.cursor()
                    cur.execute("SELECT * FROM ADMIN")
                    entries = cur.fetchall()
                    for entry in entries:
                        a = entry[0]
                        t = entry[1]
                        if a == un and t == pas:
                            session['adname'] = un
                            session['un'] = None
                            b = True
                            break
        except:
            con.rollback()
        finally:
            if b:
                return redirect("/adminhome")
            else:
                return redirect("/returnadmin")


@app.route("/adminhome")
def adminhome():
    if session['adname']:
        return render_template("adminhome.html", a=session['adname'])
    else:
        return redirect("/")


@app.route("/movies")
def movie():
    if session['adname']:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT movie_id,movie_name from MOVIE")
            entries = cur.fetchall()
        return render_template("movies.html", e=entries)
    else:
        return redirect("/")


@app.route("/edit_movie/<int:mid>")
def edit_movie(mid):
    if session['adname']:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM MOVIE WHERE MOVIE_ID = ?", str(mid))
            entry = cur.fetchone()
        return render_template("edit_movie.html", e=entry)
    else:
        return redirect("/")


@app.route("/delete_movie/<int:mid>")
def delete_movie(mid):
    if session["adname"]:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM SHOWS WHERE MOVIE_ID = ?", str(mid))
            a = cur.fetchone()
            if a[0] == 0:
                cur.execute("DELETE FROM MOVIE WHERE MOVIE_ID = ?", str(mid))
            return redirect("/movies")
    else:
        return redirect("/")


@app.route("/update_movie", methods=["GET", "POST"])
def update_movie():
    if session['adname'] and request.method == "POST":
        name = request.form["name"]
        desc = request.form["desc"]
        rate = request.form["rate"]
        lang = request.form["lang"]
        type = request.form["type"]
        dur = request.form["dur"]
        tags = request.form["tags"]
        mid = request.form["mid"]
        if not (name and desc and rate and lang and type and dur and mid):
            return redirect("/")
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("UPDATE MOVIE SET MOVIE_NAME=?,DESCRIPTION=?,RATING=?,TYPE=?,LANGUAGE=?,DURATION=?,TAGS=? WHERE MOVIE_ID = ?",
                        (name, desc, rate, type, lang, dur, tags, str(mid)))
        return redirect("/movies")
    else:
        return redirect("/")


@app.route("/add_movie")
def add_movie():
    return render_template("add_movie.html")


@app.route("/plus_movie", methods=["GET", "POST"])
def plus_movie():
    if session['adname'] and request.method == "POST":
        name = request.form["name"]
        desc = request.form["desc"]
        rate = request.form["rate"]
        lang = request.form["lang"]
        type = request.form["type"]
        dur = request.form["dur"]
        tags = request.form["tags"]
        if not (name and desc and rate and lang and type and dur and tags):
            return redirect("/")
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO MOVIE (MOVIE_NAME,DESCRIPTION,RATING,TYPE,LANGUAGE,DURATION,TAGS) VALUES (?,?,?,?,?,?,?)",
                        (name, desc, rate, type, lang, dur, tags))
        return redirect("/movies")
    else:
        return redirect("/")


@app.route("/venueShow")
def venueShow():
    if session['adname']:
        with sql.connect("database.db") as con:
            cur = con.cursor()

            cur.execute("select * from venue")
            entries = cur.fetchall()
            row_d = {}
            for entry in entries:
                if (entry[0], entry[1]) not in row_d.keys():
                    row_d[(entry[0], entry[1])] = []

            cur.execute("select s.s_id,s.venue_id,v.v_name,m.movie_name,s.timing,s.seats from shows as s, Venue as v, Movie as m where s.venue_id=v.v_id and s.movie_id=m.movie_id order by s.venue_id,s.movie_id;")
            entries = cur.fetchall()

            for entry in entries:
                row_d[(entry[1], entry[2])] = row_d[(
                    entry[1], entry[2])] + [entry]

        return render_template("venueShow.html", row_d=row_d)
    else:
        return redirect('/')


@app.route("/edit_venue/<int:vid>")
def edit_venue(vid):
    if session['adname']:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM VENUE WHERE V_ID = ?", str(vid))
            entry = cur.fetchone()
        return render_template("edit_venue.html", e=entry)
    else:
        return redirect("/")


@app.route("/update_venue", methods=["GET", "POST"])
def update_venue():
    if session['adname'] and request.method == "POST":
        v_name = request.form["name"]
        v_loc = request.form["loc"]
        vid = request.form["vid"]
        if not v_name or not v_loc or not vid:
            return redirect("/")
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute(
                "UPDATE VENUE SET V_NAME=?,Location=? WHERE V_ID = ?", (v_name, v_loc, str(vid)))
        return redirect("/venueShow")
    else:
        return redirect("/")


@app.route("/delete_venue/<int:vid>")
def delete_venue(vid):
    if session["adname"]:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM SHOWS WHERE VENUE_ID = ?", str(vid))
            a = cur.fetchone()
            if a[0] == 0:
                cur.execute("DELETE FROM VENUE WHERE V_ID = ?", str(vid))
            return redirect("/venueShow")
    else:
        return redirect("/")


@app.route("/add_venue")
def add_venue():
    return render_template("add_venue.html")


@app.route("/plus_venue", methods=["GET", "POST"])
def plus_venue():
    if session['adname'] and request.method == "POST":
        name = request.form["name"]
        loc = request.form["loc"]
        if not name or not loc:
            return redirect("/")
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO VENUE (V_NAME,Location) VALUES (?,?)", (name, loc))
        return redirect("/venueShow")
    else:
        return redirect("/")


@app.route("/edit_show/<int:sid>")
def edit_show(sid):
    if session['adname']:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            print(sid)
            cur.execute("SELECT * FROM SHOWS WHERE S_ID = ?", (str(sid),))
            entry = cur.fetchone()
            cur.execute("SELECT MOVIE_ID,MOVIE_NAME FROM MOVIE")
            entries = cur.fetchall()
        return render_template("edit_show.html", e=entry, f=entries)
    else:
        return redirect("/")


@app.route("/update_show", methods=["GET", "POST"])
def update_show():
    if session['adname'] and request.method == "POST":
        id = request.form["movie"]
        time = request.form["time"]
        seat = request.form["seat"]
        price = request.form["price"]
        sid = request.form["sid"]
        if not (id and time and seat and price and sid):
            return redirect("/")
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT TOT_SEATS FROM SHOWS")
            entry = cur.fetchone()
            print(type(entry[0]))
            op = entry[0] - int(seat)
            op = entry[0] - op
            cur.execute("UPDATE SHOWS SET MOVIE_ID=?,TIMING=?,SEATS=?,TOT_SEATS=?,PRICE=? WHERE S_ID = ?",
                        (id, time, op, seat, price, str(sid)))
        return redirect("/venueShow")
    else:
        return redirect("/")


@app.route("/delete_show/<int:sid>")
def delete_show(sid):
    if session["adname"]:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("DELETE FROM TICKET WHERE S_ID = ?", (str(sid),))
            cur.execute("DELETE FROM SHOWS WHERE S_ID = ?", (str(sid),))
            return redirect("/venueShow")
    else:
        return redirect("/")


@app.route("/add_show/<int:vid>")
def add_show(vid):
    if session['adname']:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT MOVIE_ID,MOVIE_NAME FROM MOVIE")
            entries = cur.fetchall()
        return render_template("add_show.html", f=entries, vid=vid)
    else:
        return render_template("/")


@app.route("/plus_show", methods=["GET", "POST"])
def plus_show():
    if session['adname'] and request.method == "POST":
        vid = request.form['vid']
        id = request.form["movie"]
        time = request.form["time"]
        seat = request.form["seat"]
        price = request.form["price"]
        if not (id and time and seat and price):
            return redirect("/")
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO SHOWS (VENUE_ID,MOVIE_ID,TIMING,SEATS,TOT_SEATS,PRICE) VALUES (?,?,?,?,?,?)",
                        (vid, id, time, seat, seat, price))
        return redirect("/venueShow")
    else:
        return redirect("/")


@app.route("/newUser")
def newUser():
    return render_template("sign_up.html")


@app.route("/signup", methods=['POST', 'GET'])
def signup():
    b = False
    if request.method == "POST":
        try:
            un = request.form['un']
            pas = request.form['pass']
            if not un or not pas:
                return redirect("/newUser")
            else:
                with sql.connect("database.db") as con:
                    cur = con.cursor()
                    cur.execute(
                        "INSERT INTO Users (username,password) VALUES (?,?)", (un, pas))
                    b = True
                    con.commit()

        except:
            con.rollback()
            b = False
        finally:
            if b == True:
                return redirect("/returnUser")
            else:
                return redirect("/newUser")


@app.route("/returnUser")
def returnUser():
    return render_template("log_in.html")


@app.route("/login", methods=['POST', 'GET'])
def login():
    b = False
    if request.method == "POST":
        try:
            un = request.form['un']
            pas = request.form['pass']
            if not un or not pas:
                return redirect("/returnUser")
            else:
                with sql.connect("database.db") as con:
                    cur = con.cursor()
                    cur.execute("SELECT * FROM USERS")
                    entries = cur.fetchall()
                    for entry in entries:
                        a = entry[0]
                        t = entry[1]
                        if a == un and t == pas:
                            session['un'] = un
                            session['adname'] = None
                            b = True
                            break
        except:
            con.rollback()
        finally:
            if b:
                return redirect("/home")
            else:
                return redirect("/returnUser")


@app.route("/logout")
def logout():
    session['un'] = None
    session['adname'] = None
    return redirect('/')


@app.route("/home")
def userhome():
    if session['un']:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute(
                "select t.t_id,m.movie_name,m.rating,m.type,m.language,m.duration,v.v_name,v.Location,s.timing,t.quantity,t.price from ticket as t INNER JOIN shows as s, venue as v, movie as m where t.username= ? and t.s_id = s.s_id and s.movie_id = m.movie_id and s.venue_id = v.v_id", (session['un']))
            row_d = cur.fetchall()
            return render_template("userhome.html", row_d=row_d, un=session["un"])
    else:
        return redirect("/")


@app.route("/bookshow", methods=["GET", "POST"])
def bookshow():
    if session['un']:
        if request.method == "GET" or not request.form['q']:
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("select s.s_id,v.v_name,m.movie_name,s.timing,s.seats,s.price from shows as s, venue as v, movie as m where s.venue_id=v.v_id and s.movie_id=m.movie_id order by s.venue_id,s.movie_id")
                entries = cur.fetchall()
                row_d = {}
                for entry in entries:
                    if entry[1] not in row_d.keys():
                        row_d[entry[1]] = []
                    row_d[entry[1]] = row_d[entry[1]] + [entry]

        elif request.method == "POST":
            q = request.form['q']
            q = q.split(",")
            q = [a.lower() for a in q]
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("select s.s_id,v.v_name,m.movie_name,s.timing,s.seats,s.price,m.tags,v.location from shows as s, venue as v, movie as m where s.venue_id=v.v_id and s.movie_id=m.movie_id order by s.venue_id,s.movie_id")
                entries = cur.fetchall()
                row_d = {}
                for entry in entries:
                    if entry[1] not in row_d.keys():
                        row_d[entry[1]] = []
                    if (True in [(z == y or z == x) for x in entry[6].split(",") for y in entry[7].split(",") for z in q]):
                        row_d[entry[1]] = row_d[entry[1]] + [entry]

        return render_template("bookshow.html", row_d=row_d)
    else:
        return redirect('/')


@app.route("/show/<int:sid>")
def book_ticket(sid):
    if session['un']:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute(
                "SELECT * FROM SHOWS where s_id = ? ORDER BY venue_id,movie_id", str(sid))
            entry = cur.fetchone()

            cur.execute("SELECT * FROM MOVIE where movie_id = ?",
                        str(entry[2]))
            met = cur.fetchone()

            cur.execute("SELECT * FROM VENUE where v_id = ?", str(entry[1]))
            vet = cur.fetchone()

        return render_template("book_ticket.html", m=met, v=vet, s=entry)
    else:
        return redirect("/")


@app.route("/booking", methods=['POST', 'GET'])
def booking():
    if session['un']:
        b = False
        if request.method == "POST":
            try:
                n = request.form['ticket']
                p = request.form['price']
                sid = request.form['sid']
                tot = request.form['tot']
                print(int(n))
                with sql.connect("database.db") as con:
                    cur = con.cursor()
                    if not n or not p or not sid:
                        return redirect("/bookshow")
                    cur.execute(
                        "INSERT INTO TICKET (username, s_id, quantity, price) VALUES (?,?,?,?)", (session['un'], sid, n, p))
                    cur.execute(
                        "UPDATE SHOWS SET seats = seats - ? where s_id = ? and seats > -1", (n, sid))
                    b = True

            except:
                con.rollback()
            finally:
                if b:
                    return redirect("/home")
                else:
                    return redirect("/bookshow")

    else:
        return redirect("/")


@app.route("/trouble")
def trouble():
    return render_template("e.html")


if __name__ == "__main__":
    app.run(debug=True)
