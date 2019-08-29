from flask import Flask, render_template, request
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
    board.insert(0, {"clue": "",
                     "target": -1,
                     "red_remaining": 8,
                     "blue_remaining": 9,
                     "neutral_remaining": 7,
                     "assassin_remaining": 1,
                     "difficulty": "easy",
                     "state": "choose_clue",
                     "remaining_guesses": -1,
                     "sequence": [],
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
    new_board = computer.Computer(board).make_computer_choices()
    return render_template('html/page.html', board=new_board)


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

    board[0]["clue"] = clue
    board[0]["state"] = "make_guess"
    board[0]["invalid_guesses"].append(clue)

    # print(clue, score)

    return render_template('html/page.html', board=board)


@app.route("/instructions", methods=["GET"])
def instructions():
    """
    Render the dialog box containing the instructions
    """
    return render_template('html/instructions.html')


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='127.0.0.1', port=8080, debug=True)