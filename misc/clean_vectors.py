import gensim
from libs.prediction import load_model
from tqdm import tqdm
from spellchecker import SpellChecker
import inflect
import os
from pattern3.text.en.inflect import singularize, pluralize
from copy import deepcopy
import pickle


def suitable(word, line, codenames_words, stemmed_codenames_words):
    """
    Determine if a word is suitable
    """

    # Board check
    if word in codenames_words:
        return True

    # Punctuation check
    if not word.isalpha():
        return False

    # Accent check
    if not word.isascii():
        return False

    # Vowel + y check
    if set("aeiouy").isdisjoint(word):
        return False

    # Length check
    if not 2 <= len(word) <= 12:
        return False

    # Plural check
    if pluralize(word) in codenames_words:
        return False

    # Singular check
    if singularize(word) in codenames_words:
        return False

    # Double word check
    if line.split()[1].isalpha():
        return False

    # Stem check
    if gensim.parsing.preprocessing.stem(word) in stemmed_codenames_words:
        return False

    # Containment check
    for cw in codenames_words:
        if cw in word or word in cw:
            return False

    return True


def pre_clean(in_file, tmp_file, out_file):
    """
    Clean the word vectors
    """

    suitable_words = set()
    codenames_words = set(word.strip('\n') for word in open("../static/data/codenames_words"))
    stemmed_codenames_words = set(map(gensim.parsing.preprocessing.stem, codenames_words))
    special_lines = []

    # Ignoring the errors gets rid of invalid characters
    with open(in_file, "r", errors='ignore') as input:
        with open(tmp_file, "w", encoding="utf8") as output:

            for line in tqdm(input):
                word = line.split()[0]

                # Special cases
                if word == "scuba-diving":
                    special_lines.append(line.replace("scuba-diving", "scubadiver"))
                elif word == "ice-cream":
                    special_lines.append(line.replace("ice-cream", "icecream"))
                elif word == "Lochness":
                    special_lines.append(line.replace("Lochness", "lochness"))

                # If a word is deemed suitable, write its line to file
                new_word = word.lower()
                if suitable(new_word, line, codenames_words, stemmed_codenames_words):
                    suitable_words.add(new_word)
                    output.write(line.replace(word, new_word))

        output.close()
    input.close()

    # Add the header
    add_header(tmp_file, out_file, special_lines)


def post_clean(model_file, vocab_file, top_words_file):
    """
    Clean the resultant top words
    """
    model = load_model(model_file)
    top_words = {}
    spell = SpellChecker(distance=1)
    vocabulary = set()

    for word in open("../static/data/codenames_words", "r", encoding="utf8"):
        w = word.replace(" ", "").strip("\n")
        closest_words = [a for a, b in model.similar_by_word(w, 5000) if b > 0.4]
        top_words[w] = set(closest_words)
        fixed_closest_words_1 = fix_spellings(model, closest_words, spell)
        fixed_closest_words_2 = fix_plurals(fixed_closest_words_1)
        vocabulary.update(fixed_closest_words_2)
        print(word, len(closest_words), len(fixed_closest_words_1), len(fixed_closest_words_2))

    # Retain only the relevant terms
    for w, top in top_words.items():
        top_words[w] = top.intersection(vocabulary)

    with open(vocab_file, 'wb') as f:
        pickle.dump(vocabulary, f)

    with open(top_words_file, 'wb') as f:
        pickle.dump(top_words, f)


def final_model(in_file, tmp_file, out_file, vocab_file):

    # Load codenames words and vocabulary
    codenames_words = set(word.strip('\n').replace(" ", "") for word in open("../static/data/codenames_words"))
    with open(vocab_file, 'rb') as vocab:
        vocabulary = pickle.load(vocab)
    vocab.close()

    with open(in_file, "r", encoding="utf8") as input:
        with open(tmp_file, "w", encoding="utf8") as output:
            chosen_words = vocabulary.union(codenames_words)
            for line in tqdm(input):
                word = line.split()[0]

                # Special case
                if word in chosen_words:
                    output.write(line)
        output.close()
    input.close()

    # Add the header
    add_header(tmp_file, out_file, [])


def fix_spellings(model, closest_words, spell):
    """
    Fix the incorrect spellings
    """
    misspelled = set(spell.unknown(closest_words))

    fixed_closest_words = set()
    for close_word in closest_words:
        if close_word in misspelled:
            correction = spell.correction(close_word)
            if correction in model.vocab:
                fixed_closest_words.add(spell.correction(close_word))
        else:
            fixed_closest_words.add(close_word)

    return fixed_closest_words


def fix_plurals(closest_words):
    """
    Remove plurals
    """
    fixed_closest_words = set()
    for word in closest_words:
        singular = singularize(word)
        if singular not in closest_words or singular == word:
            fixed_closest_words.add(word)
    return fixed_closest_words


def calculate_file_length(in_file):
    """
    Calculate the number of lines in a file
    """
    return sum(1 for _ in open(in_file, "r", encoding="utf8"))


def add_header(tmp_file, out_file, special_lines):
    """
    Add an appropriate word2vec header
    """
    file_length = calculate_file_length(tmp_file)
    first_line = str(file_length) + " 300\n"

    with open(tmp_file, 'r', encoding="utf8") as input:
        with open(out_file, 'w', encoding="utf8") as output:
            output.write(first_line)
            for line in special_lines:
                output.write(line)
            for line in input:
                output.write(line)
        input.close()
    output.close()

    os.remove(tmp_file)


def save_model(in_file, out_file, limit):
    """
    Load and then save a model using pre-trained weights
    """
    model = gensim.models.KeyedVectors.load_word2vec_format(in_file, binary=False, limit=limit)
    model.init_sims(replace=True)
    model.save(out_file)

    return model


def quality_check(model_paths):
    models = [load_model(m) for m in model_paths]
    for word in open("../static/data/codenames_words", "r", encoding="utf8"):
        w = word.replace(" ", "").strip("\n")
        top_words = [list(map(lambda x: x[0], m.similar_by_word(w, 5))) for m in models]
        print(w, top_words)

def pipeline(name, limit=250000):
    w2v_path = "prediction/{}.vec".format(name)
    filtered_vec_path = "prediction/{}_filtered.vec".format(name)
    filtered_path = "prediction/{}_filtered".format(name)
    vocab_path = "prediction/{}_vocab".format(name)
    # vocab_path = "prediction/joint_vocab"
    top_words_path = "prediction/{}_top_words".format(name)
    final_vec_path = "prediction/{}_final.vec".format(name)
    final_path = "prediction/{}_final".format(name)

    pre_clean(w2v_path, "tmp", filtered_vec_path)
    save_model(filtered_vec_path, filtered_path, limit)
    post_clean(filtered_path, vocab_path, top_words_path)
    final_model(filtered_vec_path, "tmp", final_vec_path, vocab_path)
    save_model(final_vec_path, final_path, limit)

def main():
    # pipeline("crawl")
    # pipeline("wiki")
    quality_check(["prediction/crawl_final", "prediction/wiki_final"])


if __name__ == "__main__":
    main()
