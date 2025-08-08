import os
import random
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from datetime import datetime, timedelta
from groq import Groq  # ✅ New import for Groq
from livereload import Server



# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Groq API Key
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


#reload#
if __name__ == '__main__':
    from livereload import Server

    server = Server(app.wsgi_app)
    server.watch('templates/*.html')   # watch HTML changes
    server.watch('static/css/*.css')   # watch CSS changes
    server.watch('static/js/*.js')     # watch JS changes
    server.serve(port=5000, host='127.0.0.1', debug=True)


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

        
        # Calculate next midnight
        next_midnight = datetime(current_dt.year, current_dt.month, current_dt.day) + timedelta(days=1)
        seconds_remaining = int((next_midnight - current_dt).total_seconds())



        return render_template(
            'wonkycal.html',
            current_dt=current_dt.strftime("%Y-%m-%d %H:%M"),
            next_midnight=next_midnight.strftime("%Y-%m-%d %H:%M"),
            seconds_remaining=seconds_remaining
        )
    return render_template('wonkycal.html')
    

# -----------------
# API: Sabogpt chatbot (Groq version)
# -----------------
@app.route('/api/sabogpt', methods=['POST'])
def sabogpt_api():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"reply": "Say something first!"})

    try:
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",  # ✅ Groq free model
            messages=[
                {
                    "role": "system",
                    "content": (
                        "roast the heck out of the user's project idea, first.,then "
                       "give a short three line, funny, and absurd reply to the user's project idea, "
                       "and then give a short three line, funny, and absurd reply to the user's project idea, "
                       "make it short"
                       "no need to specify the roasting part, just roast the heck out of the user's project idea, first.,then "
                    )
                },    
                {"role": "user", "content": user_message}
            ],
            temperature=0.9
        )
        return jsonify({"reply": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

# -----------------
# API: Life Advices (Groq version)
# -----------------
@app.route('/api/life-advices', methods=['GET'])
def life_advices_api():
    try:
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "Give one short, funny, and absurd advice based on science."
                }
            ],
            temperature=0.8
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
    guessed_age = random.randint(100, 99999)

    return jsonify({
    "you have": f"{guessed_age} seconds to live",
    "photo_url": f"/{filepath}"
})


# -----------------
# API: WonkyCal (next date + seconds left)
# -----------------
@app.route('/api/wonkycal', methods=['GET'])
def wonkycal_api():
    now = datetime.now()
    
    # Calculate next midnight
    next_midnight = datetime(current_dt.year, current_dt.month, current_dt.day) + timedelta(days=1)
    seconds_remaining = int((next_midnight - current_dt).total_seconds())



    return jsonify({
        "current_datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "next_datetime": next_midnight.strftime("%Y-%m-%d %H:%M:%S"),
        "seconds_left": seconds_remaining
    })

# -----------------
# Run App
# -----------------
if __name__ == '__main__':
    app.run(debug=True)
