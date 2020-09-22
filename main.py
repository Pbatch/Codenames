from flask import Flask, render_template, request, jsonify
import json
from libs.boardgen import Boardgen
from libs.prediction import Predictor
from libs.computer import Computer
app = Flask(__name__)


@app.route('/', methods=["POST", "GET"])
def index():
    """
    Homepage for the website.
    Create a random board.
    """
    board = Boardgen("static/data/codenames_words").board
    board.insert(0, {"difficulty": "easy",
                     "invalid_guesses": []
                     })
    return render_template('html/page.html', board=board)


@app.route("/update", methods=["POST"])
def update():
    """
    Update the page with the details from the current board
    """
    board = json.loads(request.data)
    return render_template('html/page.html', board=board)


@app.route("/computer_turn", methods=["POST"])
def computer_turn():
    """
    Get a series of computer moves
    """
    board = json.loads(request.data)
    sequence = Computer(board).generate_computer_sequence()

    json_sequence = jsonify(sequence=sequence)
    return json_sequence


@app.route("/clue", methods=["POST"])
def clue():
    """
    Generate a clue
    """
    board = json.loads(request.data)
    predictor = Predictor(relevant_words_path='static/data/relevant_words',
                          relevant_vectors_path='static/data/relevant_vectors',
                          board=board[1:],
                          invalid_guesses=set(board[0]['invalid_guesses']),
                          alpha=8.0,
                          eta=0.5)

    _clue, modal_score, targets = predictor.run()
    clue_details = jsonify(clue=_clue, targets=targets)

    return clue_details


@app.route("/instructions", methods=["GET"])
def instructions():
    """
    Render the dialog box containing the instructions
    """
    return render_template('html/instructions.html')


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='127.0.0.1', port=8080, debug=True)