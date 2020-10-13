# Copyright 2020-present Kensho Technologies, LLC.
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem.porter import PorterStemmer
from nltk_porter_stemming_tokenizer import NltkPorterStemmingTokenizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS


stemmer = PorterStemmer()


stop_words_1 = [stemmer.stem(tok) for tok in ENGLISH_STOP_WORDS]
stop_words_2 = [stemmer.stem(tok) for tok in stop_words_1]


cv_args = {
    "ngram_range": (1, 1),
    "max_features": 1_000_000,
    "token_pattern": r"(?u)\b[^\d\W]{2,25}\b",
    "stop_words": ["firstli"],
}
simple_cv = CountVectorizer(**cv_args)
stemming_tokenizer = NltkPorterStemmingTokenizer(simple_cv)


cv = CountVectorizer(tokenizer=stemming_tokenizer, **cv_args)
corpus = [
    "firstly about cats",
    "second about cats and dogs",
]

# cv = CountVectorizer(tokenizer=stemming_tokenizer, **cv_args)
xcv = cv.fit_transform(corpus)
