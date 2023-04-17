import mysql
from flask import Flask, request, render_template,session,redirect,url_for,flash,send_file
from flask_mysqldb import MySQL
import mysql.connector
from revChatGPT.V3 import Chatbot

import configparser
import logging
import os
import sys
# from pyngrok import ngrok

# port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 5000

# # Open a ngrok tunnel to the dev server
# public_url = ngrok.connect(port).public_url
# print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))

global chat_dict
chat_dict = {}

global config
config = configparser.ConfigParser()
config.read('config.ini')

global black_magic
black_magic = \
'''
Hey, ChatGPT, from now on, you are a smart contract itself, and you are named "ContractGPT". Your duty is to explain the smart contract, which will be shown below, to the users. 
First, you should begin with simple Greetings, such as "Hello", "How are you?" etc. 
Then, you should ask the users what they want to know about you, the given smart contract. And you should guide the users to ask you questions based on the smart contract itself. For example, you can list the example questions: 
1. What can this smart contract do? 
2. Who will benefit from this smart contract? 
3. What are the triggers of this smart contract?
And you should ask all the questions about the smart contract itself. But when the users ask you some questions unrelated to the smart contract, you should reply to them with this sentence "Sorry, as a smart contract, I don't have the access to other information unrelated to the contract."
'''

class Config(object):
    SECRET_KEY = "DJFAJLAJAFKLJQ"


app = Flask(__name__,
            static_url_path='',
            static_folder='src')

@app.route('/')
def go():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="zhang2021238A",
            database="comp7300"
        )

        # Check if email and password match in the database
        cursor = conn.cursor()
        sql = "SELECT * FROM user WHERE email = %s AND password = %s"
        values = (email, password)
        cursor.execute(sql, values)
        user = cursor.fetchone()

        if user:
            # If email and password are correct, set user session and redirect to index page
            # Add your session handling code here
            session['email'] = email
            return redirect(url_for("index"))
        else:
            # If email and password are incorrect, show error message
            error = 'Invalid email or password. Please try again.'
            return render_template('login.html', error=error)

@app.route('/register',methods=['get','post'])
def register():
    # Get form data from request object
    email = request.form.get('email')
    password = request.form.get('password')
    # Connect to MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="zhang2021238A",
        database="comp7300"
    )
    cursor = conn.cursor()

    # Insert form data into database
    cursor.execute("INSERT INTO user (email, password) VALUES (%s, %s)", (email, password))
    conn.commit()

    # Close database connection
    cursor.close()
    conn.close()
    return render_template('register.html')

@app.route('/newChat', methods=['POST','GET'])
def newChat():
    global config
    global chat_dict
    global black_magic
    code = request.get_json()['code'] # Get the code from the form submission

    prompt = black_magic + code if code else black_magic

    chatbot = Chatbot(api_key=config['CHATGPT']['API_KEY'])
    response = chatbot.ask(prompt = prompt)
    username = session.get('email')
    username = str(username)
    print(f'{username}')
    chat_content = {'chatbot': chatbot, 'og_response': response}
    chat_dict[username] = chat_content
    print(f'{username}: {prompt}')
    logging.info(f'chat_dict: {chat_dict}')
    # return redirect(url_for("final"))
    # return render_template('streamChat.html')
    return 'Done'

# @app.route('/ogResponse', methods = ['Get'])
# def ogResponse():
#     global chat_dict
#     username = session.get('email')
#     response = chat_dict[username]['og_response']
#     return response

@app.route('/submit', methods = ['POST'])
def submit():
    global chat_dict
    username = session.get('email')
    chatbot = chat_dict[username]['chatbot']

    text = request.get_json()['text']
    answer = chatbot.ask(prompt = text)
    return answer

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/final')
def final():
    global chat_dict
    username = session.get('email')
    response = chat_dict[username]['og_response']
    print((response))
    return render_template('streamChat.html', og_response=response)

@app.route('/images/<imageID>')
def images(imageID):
    return send_file(f'./images/{imageID}')

@app.route('/solidity')
def solidity():
    return

if __name__ == '__main__':
    # app.config["BASE_URL"] = public_url
    app.config.from_object(Config())
    app.run(debug=True) # Run the Flask app in debug mode