from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import random
import uuid

app = Flask(__name__)
app.secret_key = "supersecretkey"


db_path = 'chat.db'


@app.route('/')
def index():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    
    cur.execute('''CREATE TABLE IF NOT EXISTS chat_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        user_message TEXT,
        bot_reply TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
    )''')
    
    cur.execute("SELECT id, session_name FROM chat_sessions ORDER BY created_at DESC")
    sessions = cur.fetchall()

   
    if 'session_id' not in session:
        cur.execute("INSERT INTO chat_sessions (session_name) VALUES (?)", (f"Chat {len(sessions)+1}",))
        conn.commit()
        session['session_id'] = cur.lastrowid

    cur.execute("SELECT user_message, bot_reply FROM chat_messages WHERE session_id = ?", (session['session_id'],))
    chats = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('index.html', sessions=sessions, chats=chats)


@app.route('/get', methods=['POST'])
def chatbot_response():
    user_message = request.form['msg']
    session_id = session.get('session_id')

    
    responses = {
        "hello": ["Hey there!", "Hello 👋", "Hi! How can I assist you today?"],
        "bye": ["Goodbye 👋", "See you later!", "Take care!"],
        "name": ["I’m Chatly, your friendly assistant 🤖"],
        "default": ["Hmm, I didn’t get that 🤔", "Can you rephrase?", "I'm learning more each day!"]
    }

    bot_reply = random.choice(responses.get(user_message.lower(), responses["default"]))

   
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("INSERT INTO chat_messages (session_id, user_message, bot_reply) VALUES (?, ?, ?)",
                (session_id, user_message, bot_reply))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'reply': bot_reply})

@app.route('/chat/<int:session_id>')
def load_chat(session_id):
    session['session_id'] = session_id
    return redirect(url_for('index'))


@app.route('/new_chat')
def new_chat():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM chat_sessions")
    count = cur.fetchone()[0]
    cur.execute("INSERT INTO chat_sessions (session_name) VALUES (?)", (f"Chat {count+1}",))
    conn.commit()
    session['session_id'] = cur.lastrowid
    cur.close()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
