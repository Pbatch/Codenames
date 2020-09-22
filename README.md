# Codenames

Update: The website has been closed due to hosting costs

## Description

* In Codenames two teams compete by each having a Spymaster give one word clues which can point to multiple words on the board. 
* The other players on the team attempt to guess their team's words while avoiding the words of the other team.
* In this project we demonstrate that a computer can successfully play the role of a good Spymaster.

## Explanation
* Word2vec is a model that takes a corpus of words and embeds it in a vector space, with similar words having a higher score under the cosine metric.

Note - The user must specify 'target', the number of words the model should aim to link

## Preprocessing

Generating your own word2vec model is expensive, so we prefer to download a pretrained one:

https://fasttext.cc/docs/en/english-vectors.html

These models are quite rough and need cleaning.
Issues include:
* Repeated words in different cases
* Words which relate grammatically to board words
* Misspelled words
* etc.

Full details are given in:

[clean_vectors.py](preprocessing/clean_vectors.py)

## Prediction

Once we've cleaned the model we are ready to generate clues for a board.
The model scores clues in 3 stages.
1) Negative similarity from the guess to red, neutral and assassin words
2) Similarity from the guess to blue words
3) 'Cluster score' of the blue words that the guess links + the guess.

It is important to note that we threshold similarities in steps 1) and 2).
Set the similarity score to be 1 if s >= 0.4, and 0 otherwise. We do this because any
similarity score below 0.4 is essentially noise.

Full details are given in:

[prediction.py](libs/prediction.py)

## Other

[boardgen.py](libs/boardgen.py) generates a board

[computer.py](libs/computer.py) generates opponent guesses





