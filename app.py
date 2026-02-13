import os
from flask import Flask, render_template, request, redirect
from cs50 import SQL

app = Flask(__name__)

# Connect to database (absolute path so it always uses THIS folder's fittrack.db)
db_path = os.path.join(os.path.dirname(__file__), "fittrack.db")
db = SQL("sqlite:///" + db_path)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/log", methods=["GET", "POST"])
def log():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        workout_type = (request.form.get("type") or "").strip()
        duration = (request.form.get("duration") or "").strip()
        notes = (request.form.get("notes") or "").strip()

        if not name or not workout_type or not duration:
            return redirect("/log")

        # Insert workout
        workout_id = db.execute(
            "INSERT INTO workouts (name, workout_type, duration, notes) VALUES (:name, :workout_type, :duration, :notes)",
            name=name,
            workout_type=workout_type,
            duration=duration,
            notes=notes
        )

        # Insert exercises
        exercise_names = request.form.getlist("exercise_name[]")
        sets_list = request.form.getlist("sets[]")
        reps_list = request.form.getlist("reps[]")
        weights_list = request.form.getlist("weight[]")

        for i in range(len(exercise_names)):
            ex_name = (exercise_names[i] or "").strip()
            if ex_name == "":
                continue

            sets_val = (sets_list[i] if i < len(sets_list) else "") or ""
            reps_val = (reps_list[i] if i < len(reps_list) else "") or ""
            weight_val = (weights_list[i] if i < len(weights_list) else "") or ""

            db.execute(
                "INSERT INTO exercises (workout_id, exercise_name, sets, reps, weight) "
                "VALUES (:workout_id, :exercise_name, :sets, :reps, :weight)",
                workout_id=workout_id,
                exercise_name=ex_name,
                sets=sets_val,
                reps=reps_val,
                weight=weight_val
            )

        return redirect("/progress")

    return render_template("log.html")


@app.route("/progress")
def progress():
    workouts = db.execute("SELECT * FROM workouts ORDER BY id DESC")

    # Add exercise lists to each workout
    for workout in workouts:
        workout["exercises"] = db.execute(
            "SELECT * FROM exercises WHERE workout_id = :workout_id",
            workout_id=workout["id"]
        )

    return render_template("progress.html", workouts=workouts)


@app.route("/delete/<int:id>")
def delete(id):
    db.execute("DELETE FROM exercises WHERE workout_id = :workout_id", workout_id=id)
    db.execute("DELETE FROM workouts WHERE id = :id", id=id)
    return redirect("/progress")


if __name__ == "__main__":
    app.run(debug=True)
