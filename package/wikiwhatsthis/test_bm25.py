# Copyright 2020-present Kensho Technologies, LLC.
from sklearn.feature_extraction.text import CountVectorizer
from bm25_transformer import BM25Transformer

cv = CountVectorizer()
corpus = [
    "first about cats",
    "second about cats and dogs",
]

xcv = cv.fit_transform(corpus)
bm25 = BM25Transformer(use_idf=True)
bm25.fit(xcv)
xbm25 = bm25.fit_transform(xcv)
