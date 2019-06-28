import gensim
from board import Board
from itertools import combinations
import argparse


def load_model(in_file, limit, binary_mode):
    """
    Load a model using pre-trained weights
    """
    model = gensim.models.KeyedVectors.load_word2vec_format(in_file, binary=binary_mode, limit=limit)
    return model


class Predictor:
    def __init__(self, board, model, vocabulary, blue, red, assassin, target):
        self.board = board
        self.model = model
        self.vocabulary = vocabulary
        self.target = target
        self.blue = blue
        self.red = red
        self.assassin = assassin
        self.cluster_dict = self.make_cluster_dict()

    def similarity(self, first_word, second_word):
        """
        Determine how similar two words are
        """
        try:
            return self.model.similarity(first_word, second_word)
        except KeyError:
            return 0

    def make_cluster_dict(self):
        """
        Generate the scores for clusters of size target

        This dictionary will save unnecessary computation time later on
        """
        pairwise_scores = {}
        for pair in combinations(self.blue, 2):
            pairwise_scores[pair] = self.similarity(pair[0], pair[1])

        cluster_dict = {}
        for blue_words in combinations(self.blue, self.target):
            cluster_dict[blue_words] = sum([pairwise_scores[p] for p in combinations(blue_words, 2)])
        return cluster_dict

    def guess_score(self, guess, mode):
        """
        Generate a score for a guess

        Simple mode
        -----------
        Idea - A clue is only as good as the worst word
        1.) Calculate the similarity scores for all the words in blue
        2.) Set the blue score to be the minimum score of the top 'target' words

        Cluster mode
        ------------
        Idea -  Clues should be clusters of similar words,
        rather than just words that link to a guess.
        1.) Calculate a score for each cluster of size 'target' of blue words
        2.) This score is the sum of pairwise connections in the cluster
        3.) For comparison sake divide by the cluster size
        """
        for w in self.board:
            if w in guess or guess in w:
                return -float('inf')

        if mode == "simple":
            blue_similarities = [self.similarity(w, guess) for w in self.blue]
            blue_score = sorted(blue_similarities)[-self.target]
        else:
            cluster_scores = []
            for blue_words in combinations(self.blue, self.target):
                tmp_score = self.cluster_dict[blue_words] \
                            + sum([self.similarity(guess, w) for w in blue_words])
                cluster_scores.append(tmp_score)

            cluster_size = self.target * (self.target + 1) / 2
            blue_score = max(cluster_scores) / cluster_size

        bad_similarities = [self.similarity(w, guess) for w in self.red] \
                           + [self.similarity(self.assassin, guess)]
        bad_score = max(bad_similarities)

        score = blue_score - bad_score
        return score

    def get_sorted_guesses(self, mode):
        """
        Get the guesses and their scores sorted in descending order
        """
        guesses = [(self.guess_score(guess, mode), guess) for guess in self.vocabulary]
        sorted_guesses = sorted(guesses)[::-1]

        return sorted_guesses

    def print_influence(self, guess):
        """
        Print what influenced the best guess decision
        """
        blue_scores = [(self.similarity(w, guess), w) for w in self.blue]
        bad_scores = [(self.similarity(w, guess), w) for w in self.red] \
                     + [(self.similarity(self.assassin, guess), self.assassin)]

        print("Positive influences")
        for (score, word) in sorted(blue_scores)[-self.target:]:
            print("{}: {:.3f}\t".format(word, score), end="")
        print("\nNegative influences")
        for (score, word) in sorted(bad_scores)[-self.target:]:
            print("{}: {:.3f}\t".format(word, score), end="")
        print("\n")


def main():
    parser = argparse.ArgumentParser(description='Create a Codenames board.'
                                                 'Generate potential guesses for both teams.')
    parser.add_argument('codenames_words', type=str,
                        help='The file location of Codenames words')
    parser.add_argument('training_vectors', type=str,
                        help='The file location of the training vectors')
    parser.add_argument('common_words', type=str,
                        help='The file location of common words')
    parser.add_argument('-target', type=int, default=2,
                        help='The number of words the clues will try to match to')
    parser.add_argument('-guesses', type=int, default=1,
                        help='The number of potential clues to print out')
    parser.add_argument('-mode',  type=str, default='cluster',
                        choices=['cluster', 'simple'],
                        help='The algorithm used to create the clues')
    parser.add_argument('-print_board', type=bool,
                        help='Set to False if you do not want to print the board.'
                             'The colours might fail in a terminal', default=True)
    args = parser.parse_args()

    model = load_model(args.training_vectors, binary_mode=False, limit=10000)
    common_words = [word.strip().lower() for word in open(args.common_words)]
    vocabulary = set(model.vocab).intersection(set(common_words))

    board = Board(args.codenames_words, args.print_board)
    board, blue, red, _, assassin = board.get_board_and_classes()

    blue_predictor = Predictor(board, model, vocabulary, blue, red, assassin, args.target)
    sorted_blue_guesses = blue_predictor.get_sorted_guesses(mode=args.mode)[:args.guesses]

    print("Blue team\n---------")
    for score, guess in sorted_blue_guesses:
        print("Guess: {}\nScore: {:.3f}".format(guess, score))
        blue_predictor.print_influence(guess)

    red_predictor = Predictor(board, model, vocabulary, red, blue, assassin, args.target)
    sorted_red_guesses = red_predictor.get_sorted_guesses(mode=args.mode)[:args.guesses]

    print("Red team\n--------")
    for score, guess in sorted_red_guesses:
        print("Guess: {}\nScore: {:.3f}".format(guess, score))
        red_predictor.print_influence(guess)


if __name__ == "__main__":
    main()




