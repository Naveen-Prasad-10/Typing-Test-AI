import os  # <- needed for PORT
from flask import Flask, render_template, request, redirect, url_for, session
import nltk
import random
import time
from nltk.corpus import brown
from nltk.tokenize import word_tokenize

nltk.download('brown')
nltk.download('punkt')

app = Flask(__name__)
app.secret_key = "typingtestsecret"  # Needed for sessions

# Function to generate a random sentence
def generate_sentence():
    sentence = random.choice(brown.sents())
    return " ".join(sentence)

# Function to calculate WPM
def calculate_wpm(typed_text, start_time, end_time):
    words = word_tokenize(typed_text)
    num_words = len(words)
    elapsed_minutes = (end_time - start_time) / 60
    if elapsed_minutes == 0:
        elapsed_minutes = 1/60
    wpm = num_words / elapsed_minutes
    return wpm, num_words

# Function to calculate accuracy
def calculate_accuracy(original, typed):
    original_words = word_tokenize(original)
    typed_words = word_tokenize(typed)
    correct = sum(o == t for o, t in zip(original_words, typed_words))
    accuracy = (correct / len(original_words)) * 100
    return accuracy

@app.route('/')
def index():
    session['all_wpm'] = []
    session['all_words'] = []
    session['all_accuracy'] = []

    sentence = generate_sentence()
    session['current_sentence'] = sentence
    session['start_time'] = time.time()
    return render_template("index.html", sentence=sentence)

@app.route('/submit', methods=['POST'])
def submit():
    typed_text = request.form['typed_text']
    start_time = session['start_time']
    end_time = time.time()
    original_sentence = session['current_sentence']

    wpm, num_words = calculate_wpm(typed_text, start_time, end_time)
    accuracy = calculate_accuracy(original_sentence, typed_text)

    session['all_wpm'].append(wpm)
    session['all_words'].append(num_words)
    session['all_accuracy'].append(accuracy)

    return render_template("results.html", wpm=wpm, num_words=num_words,
                           accuracy=accuracy, avg=False)

@app.route('/next', methods=['POST'])
def next_round():
    choice = request.form['choice'].strip().lower()
    if choice != 'y':
        avg_wpm = sum(session['all_wpm']) / len(session['all_wpm'])
        avg_words = sum(session['all_words']) / len(session['all_words'])
        avg_accuracy = sum(session['all_accuracy']) / len(session['all_accuracy'])
        rounds = len(session['all_wpm'])
        return render_template("results.html", avg=True, avg_wpm=avg_wpm,
                               avg_words=avg_words, avg_accuracy=avg_accuracy,
                               rounds=rounds)
    else:
        sentence = generate_sentence()
        session['current_sentence'] = sentence
        session['start_time'] = time.time()
        return render_template("index.html", sentence=sentence)

# ✅ Deployment-friendly server start
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use Railway's PORT
    app.run(host='0.0.0.0', port=port, debug=True)
