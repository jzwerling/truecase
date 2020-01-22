import pickle
import os
import math
import string
import spacy


class text_token(object):
    def __init__(self, token_text, type):
        self.text = token_text
        self.type = type

    def __str__(self):
        return ("{} : {}".format(self.text, self.type))

class TrueCaser(object):
    def __init__(self, dist_file_path=None):

        if dist_file_path is None:
            dist_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/english.dist')

        with open(dist_file_path, 'rb') as distributions_file:
            pickle_dict = pickle.load(distributions_file)
            self.uni_dist = pickle_dict['uni_dist']
            self.backward_bi_dist = pickle_dict['backward_bi_dist']
            self.forward_bi_dist = pickle_dict['forward_bi_dist']
            self.trigram_dist = pickle_dict['trigram_dist']
            self.word_casing_lookup = pickle_dict['word_casing_lookup']

    def get_score(self, prev_token, possible_token, next_token):
        pseudo_count = 5.0

        # Get Unigram Score
        nominator = self.uni_dist[possible_token] + pseudo_count
        denominator = 0
        for alternativeToken in self.word_casing_lookup[possible_token.lower()]:
            denominator += self.uni_dist[alternativeToken] + pseudo_count

        unigram_score = nominator / denominator

        # Get Backward Score
        bigram_backward_score = 1
        if prev_token is not None:
            nominator = self.backward_bi_dist[prev_token + '_' + possible_token] + pseudo_count
            denominator = 0
            for alternativeToken in self.word_casing_lookup[possible_token.lower()]:
                denominator += self.backward_bi_dist[prev_token + '_' + alternativeToken] + pseudo_count

            bigram_backward_score = nominator / denominator

        # Get Forward Score
        bigram_forward_score = 1
        if next_token is not None:
            next_token = next_token.lower()  # Ensure it is lower case
            nominator = self.forward_bi_dist[possible_token + "_" + next_token] + pseudo_count
            denominator = 0
            for alternativeToken in self.word_casing_lookup[possible_token.lower()]:
                denominator += self.forward_bi_dist[alternativeToken + "_" + next_token] + pseudo_count

            bigram_forward_score = nominator / denominator

        # Get Trigram Score
        trigram_score = 1
        if prev_token is not None and next_token != None:
            next_token = next_token.lower()  # Ensure it is lower case
            nominator = self.trigram_dist[prev_token + "_" + possible_token + "_" + next_token] + pseudo_count
            denominator = 0
            for alternativeToken in self.word_casing_lookup[possible_token.lower()]:
                denominator += self.trigram_dist[prev_token + "_" + alternativeToken + "_" + next_token] + pseudo_count

            trigram_score = nominator / denominator

        result = math.log(unigram_score) + math.log(bigram_backward_score) + math.log(bigram_forward_score) + math.log(
            trigram_score)

        return result

    def get_true_case(self, sentence, out_of_vocabulary_token_option='title'):
        """
        Returns the true case for the passed tokens.
        @param tokens: Tokens in a single sentence
        @param outOfVocabulariyTokenOption:
            title: Returns out of vocabulary (OOV) tokens in 'title' format
            lower: Returns OOV tokens in lower case
            as-is: Returns OOV tokens as is
        """
        nlp = spacy.load('en_core_web_sm')
        
        doc = nlp(sentence)

        token_text = []
        for t in doc: 
            cat = ''
            if t.is_space:
                cat = 'space'
            elif t.is_digit:
                cat = 'digit'
            elif t.is_punct:
                cat = 'punctuation'
            else:
                cat = 'word'
            token_text.append(text_token(t.text, cat))
            if t.whitespace_:
                cat = 'whitespace'
                token_text.append(text_token(t.whitespace_, cat))


        tokens_true_case = []

        for token_idx, tt in enumerate(token_text):
            if tt.type in ['space', 'digit', 'punctuation', 'whitespace']:
                tokens_true_case.append(tt.text)
            else:
                token = tt.text.lower()
                if token in self.word_casing_lookup:
                    if len(self.word_casing_lookup[token]) == 1:
                        tokens_true_case.append(list(self.word_casing_lookup[token])[0])
                    else:
                        prev_token = tokens_true_case[token_idx - 2] if token_idx > 1 else None
                        next_token = token_text[token_idx + 2].text if token_idx < len(token_text) - 2 else None

                        best_token = None
                        highest_score = float("-inf")

                        for possible_token in self.word_casing_lookup[token]:
                            score = self.get_score(prev_token, possible_token, next_token)

                            if score > highest_score:
                                best_token = possible_token
                                highest_score = score

                        tokens_true_case.append(best_token)

                    if token_idx == 0:
                        tokens_true_case[0] = tokens_true_case[0].title();

                else:  # Token out of vocabulary
                        tokens_true_case.append(token)

        return ''.join(tokens_true_case)



caser = TrueCaser(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/english.dist'))

text = "oddly cased text \r\n  here."
print(caser.get_true_case(text, 'title'))
