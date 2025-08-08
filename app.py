import os
import random
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import openai

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Routes for pages
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

# API: Sabogpt chatbot
@app.route('/api/sabogpt', methods=['POST'])
def sabogpt_api():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"reply": "Say something first!"})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are Sabogpt, a silly, sarcastic, and slightly nonsensical chatbot."},
            {"role": "user", "content": user_message}
        ]
    )
    return jsonify({"reply": response.choices[0].message.content})

# API: Life Advices
@app.route('/api/life-advices', methods=['GET'])
def life_advices_api():
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Give one short, funny, or absurd life advice."}
        ]
    )
    return jsonify({"advice": response.choices[0].message.content})

# API: Age Guesser (random age)
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

if __name__ == '__main__':
    app.run(debug=True)
