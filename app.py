"""
app.py
Flask frontend
"""
from flask import Flask
from flask import render_template, request
from flask_restful import Api, Resource
from multiprocessing import Process, Pipe
from backend import main, new_person

PUBLIC = False

app = Flask(__name__)
api = Api(app)
pipe, card_listener = Pipe()


def start_card_listener():
    Process(target=lambda x: x.send(main()), args=(pipe,)).start()


class CardData(Resource):

    def get(self):
        if card_listener.poll():
            return card_listener.recv()
        else:
            return {'name': "Waiting...",
                    'uid': "",
                    'recognized': 'yes'}


api.add_resource(CardData, '/card-data')


@app.route('/')
def index():
    if request.method == 'POST':
        post_request = request.form['name']
        new_person(uid, post_request)  # FIXME uh oh
        error = "Successfully registered " + post_request
        return render_template('index.html', error=error)
    else:
        return render_template('index.html')


if __name__ == '__main__':
    if PUBLIC:
        app.run(host='0.0.0.0')
    else:
        app.run(port=5000, debug=True)
