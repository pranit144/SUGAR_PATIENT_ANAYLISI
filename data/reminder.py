from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure secret key

# Telegram Bot Details
BOT_TOKEN = '8193042133:AAHBbDMvrwVnxngmA0oxRnVJX0MI8dlsaq8'
CHAT_ID = '1445155138'
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# Set up the scheduler to handle reminder jobs
scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


def send_telegram_message(message):
    """
    Sends a personalized message to the specified Telegram chat.
    """
    data = {'chat_id': CHAT_ID, 'text': message}
    try:
        response = requests.post(TELEGRAM_API_URL, data=data)
        print("Telegram API response:", response.text)
    except Exception as e:
        print("Error sending Telegram message:", e)


@app.route('/', methods=['GET', 'POST'])
def index():
    scheduled_entries = {"medicine": [], "exercise": []}

    if request.method == 'POST':
        # Retrieve multiple Medicine Reminder entries
        med_names = request.form.getlist('med_name')
        dosages = request.form.getlist('dosage')
        med_times = request.form.getlist('med_time')
        frequencies = request.form.getlist('frequency')
        instructions = request.form.getlist('additional_instructions')

        # Retrieve multiple Exercise Reminder entries
        exercise_types = request.form.getlist('exercise_type')
        durations = request.form.getlist('duration')
        exercise_times = request.form.getlist('exercise_time')
        exercise_specs_list = request.form.getlist('exercise_specs')

        now = datetime.datetime.now()
        # Process each Medicine entry
        for i in range(len(med_names)):
            try:
                med_time_obj = datetime.datetime.strptime(med_times[i], "%H:%M").time()
            except ValueError:
                flash("Time format error in Medicine entry. Please use HH:MM format.")
                return redirect(url_for('index2'))
            med_datetime = datetime.datetime.combine(now.date(), med_time_obj)
            if med_datetime < now:
                med_datetime += datetime.timedelta(days=1)
            med_message = (
                f"Hi! Here is your Medicine Reminder:\n"
                f"Medicine: {med_names[i]}\n"
                f"Dosage: {dosages[i]}\n"
                f"Frequency: {frequencies[i]}\n"
                f"Instructions: {instructions[i]}"
            )
            # Schedule the medicine reminder job
            scheduler.add_job(send_telegram_message, 'date', run_date=med_datetime, args=[med_message])
            scheduled_entries["medicine"].append({
                "medicine": med_names[i],
                "dosage": dosages[i],
                "time": med_datetime.strftime("%Y-%m-%d %H:%M"),
                "frequency": frequencies[i],
                "instructions": instructions[i]
            })

        # Process each Exercise entry
        for i in range(len(exercise_types)):
            try:
                exercise_time_obj = datetime.datetime.strptime(exercise_times[i], "%H:%M").time()
            except ValueError:
                flash("Time format error in Exercise entry. Please use HH:MM format.")
                return redirect(url_for('index2'))
            exercise_datetime = datetime.datetime.combine(now.date(), exercise_time_obj)
            if exercise_datetime < now:
                exercise_datetime += datetime.timedelta(days=1)
            exercise_message = (
                f"Hi! Here is your Exercise Reminder:\n"
                f"Exercise: {exercise_types[i]}\n"
                f"Duration: {durations[i]}\n"
                f"Specifications: {exercise_specs_list[i]}"
            )
            # Schedule the exercise reminder job
            scheduler.add_job(send_telegram_message, 'date', run_date=exercise_datetime, args=[exercise_message])
            scheduled_entries["exercise"].append({
                "exercise": exercise_types[i],
                "duration": durations[i],
                "time": exercise_datetime.strftime("%Y-%m-%d %H:%M"),
                "specs": exercise_specs_list[i]
            })

        flash("Reminders scheduled successfully!")
        return render_template('index2.html', scheduled_entries=scheduled_entries)

    return render_template('index2.html', scheduled_entries=scheduled_entries)


if __name__ == '__main__':
    app.run(debug=True,port=5005)
