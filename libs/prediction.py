import gensim
from itertools import combinations, chain
import argparse
import pickle


def load_model(in_file):
    """
    Load a pretrained model
    """
    model = gensim.models.KeyedVectors.load(in_file, mmap="r")
    return model


class Predictor:
    """
    Generate clues for the blue team
    """
    def __init__(self, board, models, vocab_path, target, invalid_guesses):
        """
        Parameters
        ----------
        board: json
            The current board state
        models: list
            The word2vec models used to compute word distances
        vocab_path: str
            The path to the vocabulary
        target: int
            The number of words to try and link
        invalid_guesses: set
            Clues which have already been given
        """
        self.models = models
        self.target = target
        self.vocab_path = vocab_path
        self.board = board
        self.invalid_guesses = invalid_guesses

        self.words = self.get_words()
        self.blue, self.red, self.neutral, self.assassin = self.get_types()

        self.pairwise_scores = self.calculate_pairwise_scores()
        self.valid_guesses = self.get_valid_guesses()

    def get_words(self):
        """
        Extract the words from the cards
        """
        words = [card["name"].replace(" ", "") for card in self.board if not card["active"]]
        return words

    def get_types(self):
        """
        Extract the types from the cards
        """
        blue = []
        red = []
        neutral = []
        assassin = ""
        for card in self.board:
            name = card["name"].replace(" ", "")
            if card["type"] == "blue" and not card["active"]:
                blue.append(name)
            if card["type"] == "red" and not card["active"]:
                red.append(name)
            if card["type"] == "neutral" and not card["active"]:
                neutral.append(name)
            if card["type"] == "assassin" and not card["active"]:
                assassin = name
        return blue, red, neutral, assassin

    def get_valid_guesses(self):
        """
        Get the relevant valid guesses
        """
        with open(self.vocab_path, "rb") as f:
            top_words_dictionary = pickle.load(f)
        potential_guesses = set(chain.from_iterable(top_words_dictionary[w] for w in self.blue))
        valid_guesses = potential_guesses.difference(self.invalid_guesses)

        return valid_guesses

    def similarity(self, first_word, second_word):
        """
        Determine how similar two words are
        """
        total_score = 0
        for model in self.models:
            try:
                score = model.similarity(first_word, second_word)
                if score >= 0.4:
                    total_score += score
            except KeyError:
                pass

        return total_score

    def calculate_pairwise_scores(self):
        """
        Generate the pairwise scores

        This dictionary will save unnecessary computation time later on
        """
        pairwise_scores = {}
        for pair in combinations(self.blue, 2):
            pairwise_scores[pair] = self.similarity(pair[0], pair[1])
        return pairwise_scores

    def guess_score(self, guess):
        """
        Generate a score for a guess

        The first component is the number of relevant red + neutral + assassin words
        The second component is the number of relevant blue words
        The final component is a measure of how well the clue and the relevant blue words link
        """

        if guess in self.words:
            return [float('-inf'), float('-inf')]

        score = [0, 0, 0]

        bad_similarities = [(w, self.similarity(guess, w)) for w in self.red + self.neutral + [self.assassin]]
        relevant_bad_words = [w for w, s in bad_similarities if s != 0]

        score[0] = -len(relevant_bad_words)

        blue_similarities = [(w, self.similarity(guess, w)) for w in self.blue]
        relevant_blue_words = {w: s for w, s in blue_similarities if s != 0}

        score[1] = min(self.target, len(relevant_blue_words))

        for blue_words in combinations(relevant_blue_words.keys(), score[1]):
            pairs = combinations(blue_words, 2)
            cluster_score = sum(self.pairwise_scores[(a, b)] for a, b in pairs)
            guess_score = sum(relevant_blue_words[w] for w in blue_words)
            total_score = cluster_score + guess_score
            if total_score >= score[2]:
                score[2] = total_score

        return score

    def get_best_guess_and_score(self):
        """
        Get the best guess and its score
        """
        guess_scores = ((self.guess_score(g), g) for g in self.valid_guesses)
        best_score, best_guess = max(guess_scores)

        return best_score, best_guess


def main():
    parser = argparse.ArgumentParser(description='Create a Codenames board.'
                                                 'Generate potential guesses for both teams.')
    parser.add_argument('codenames_words', type=str,
                        help='The file location of Codenames words')
    parser.add_argument('training_vectors', type=str,
                        help='The file location of the pretrained model')
    args = parser.parse_args()

    model = load_model(args.training_vectors)
    for word in open("../static/codenames_words"):
        w = word.strip("\n").replace(" ", "")
        if w not in model.vocab:
            print(w)

    with open("../static/top_words", "rb") as f:
        top_words_dict = pickle.load(f)

    for w in set(chain.from_iterable(top_words_dict.values())):
        if w not in model.vocab:
            print(w)

if __name__ == "__main__":
    main()











