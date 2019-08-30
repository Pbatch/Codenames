from flask import Flask, render_template, request, jsonify
import sys
import json
sys.path.insert(0, 'libs')
import boardgen
import prediction
import computer
app = Flask(__name__)


@app.route('/', methods=["POST", "GET"])
def index():
    """
    Homepage for the website.
    Create a random board.
    """
    board = boardgen.Boardgen("static/data/codenames_words").board
    board.insert(0, {"target": -1,
                     "difficulty": "easy",
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
    sequence = computer.Computer(board).generate_computer_sequence()

    json_sequence = jsonify(sequence=sequence)
    return json_sequence


@app.route("/clue", methods=["POST"])
def clue():
    """
    Generate a clue
    """
    board = json.loads(request.data)
    models = [prediction.load_model("static/data/{}_final".format(name)) for name in ["wiki"]]

    predictor = prediction.Predictor(board=board[1:],
                                     models=models,
                                     vocab_path="static/data/wiki_top_words",
                                     target=board[0]["target"],
                                     invalid_guesses=set(board[0]["invalid_guesses"]))

    score, clue = predictor.get_best_guess_and_score()
    # print(clue, score)

    return clue


@app.route("/instructions", methods=["GET"])
def instructions():
    """
    Render the dialog box containing the instructions
    """
    return render_template('html/instructions.html')


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='127.0.0.1', port=8080, debug=True)