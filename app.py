import os
import random
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import openai
from datetime import datetime, timedelta


# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# -----------------
# Routes for pages
# -----------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sabogpt')
def sabogpt_page():
    return render_template('sabogpt.html')

@app.route('/ageguesser', methods=['GET', 'POST'])
def age_guesser_page():
    return render_template('ageguesser.html')

@app.route('/lifeadvices')
def life_advices_page():
    return render_template('lifeadvices.html')

@app.route('/wonkycal', methods=['GET', 'POST'])

def wonkycal():
    if request.method == 'POST':
        # Get date and time from form
        date_str = request.form.get('date')
        time_str = request.form.get('time')

        try:
            current_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            return render_template('wonkycal.html', error="Invalid date/time format!")

        # Calculate next day
        next_day = current_dt + timedelta(days=1)
        seconds_remaining = int((next_day - current_dt).total_seconds())

        return render_template(
            'wonkycal.html',
            current_dt=current_dt.strftime("%Y-%m-%d %H:%M"),
            next_day=next_day.strftime("%Y-%m-%d %H:%M"),
            seconds_remaining=seconds_remaining
        )
    return render_template('wonkycal.html')
    

# -----------------
# API: Sabogpt chatbot
# -----------------
from openai import OpenAI
from flask import Flask, request, jsonify


client = OpenAI()

# Sabogpt
@app.route('/api/sabogpt', methods=['POST'])
def sabogpt_api():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"reply": "Say something first!"})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are Sabogpt, we are in a hackathon and we need to sabotage each other's projects so give sarcastic roasts and ways to mess up others' projects, keep answers under 100 words."
                },
                {"role": "user", "content": user_message}
            ]
        )
        return jsonify({"reply": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})


# Life Advices
@app.route('/api/life-advices', methods=['GET'])
def life_advices_api():
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Give one short, funny, or absurd life advice."
                }
            ]
        )
        return jsonify({"advice": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"advice": f"Error: {str(e)}"})


# -----------------
# API: Age Guesser (random age)
# -----------------
@app.route('/api/guess-age', methods=['POST'])
def guess_age():
    if 'photo' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['photo']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Save uploaded file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    
    # Random age
    guessed_age = random.randint(1, 100)
    
    return jsonify({"age": guessed_age, "photo_url": f"/{filepath}"})

# -----------------
# API: WonkyCal (next date + seconds left)
# -----------------
@app.route('/api/wonkycal', methods=['GET'])
def wonkycal_api():
    now = datetime.now()
    next_day = now + timedelta(days=1)
    seconds_left = int((next_day - now).total_seconds())

    return jsonify({
        "current_datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "next_datetime": next_day.strftime("%Y-%m-%d %H:%M:%S"),
        "seconds_left": seconds_left
    })

# -----------------
# Run App
# -----------------
if __name__ == '__main__':
    app.run(debug=True)
