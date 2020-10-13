# Copyright 2020-present Kensho Technologies, LLC.
import numpy as np
import pandas as pd
import scipy.sparse
from typing import Iterable, List
import warnings

from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message="Your stop_words may be inconsistent with your preprocessing.",
)


class ExplicitTopicModel:
    def __init__(
        self,
        cv: CountVectorizer,
        xdocterm: scipy.sparse.csr_matrix,
        topic_df: pd.DataFrame,
        stemmer: SnowballStemmer,
    ) -> None:
        self.cv = cv
        self.xdocterm = xdocterm
        self.topic_df = topic_df
        self.stemmer = stemmer

        self.analyzer = cv.build_analyzer()
        self.indx2tok = np.array(cv.get_feature_names())
        self.tok2indx = cv.vocabulary_

        print(
            "creating explicit topic model (topics={}, tokens={})".format(
                xdocterm.shape[0], xdocterm.shape[1]
            )
        )

    def _stem_and_tokenize(self, text: str) -> List[str]:
        return [self.stemmer.stem(token) for token in self.analyzer(text)]

    def _tokenize(self, text: str) -> List[str]:
        return self.analyzer(text)

    def topn_topics_from_text(self, text: str, topn: int = 10, thresh: float = 0.0) -> pd.DataFrame:
        tokens = self._stem_and_tokenize(text)
        topic_vector = self.topic_vec_from_tokens(tokens)
        return self.topn_topics_from_topic_vec(topic_vector, topn=topn, thresh=thresh)

    def topn_topics_from_tokens(
        self, tokens: Iterable[str], topn: int = 10, thresh: float = 0.0
    ) -> pd.DataFrame:
        topic_vector = self.topic_vec_from_tokens(tokens)
        return self.topn_topics_from_topic_vec(topic_vector, topn=topn, thresh=thresh)

    def topn_topics_from_topic_vec(
        self, topic_vector: np.ndarray, topn: int = 10, thresh: float = 0.0
    ) -> pd.DataFrame:
        topic_indxs = np.argsort(-topic_vector)[:topn]
        top_topics_df = self.topic_df.iloc[topic_indxs].copy()
        topic_scores = topic_vector[topic_indxs]
        top_topics_df["score"] = topic_scores
        return top_topics_df[top_topics_df["score"] > thresh].copy()

    def topic_vec_from_tokens(self, tokens: Iterable[str]) -> np.ndarray:
        token_indices = [self.tok2indx[token] for token in tokens if token in self.tok2indx]
        norm = max(1, len(token_indices))
        topic_vector = np.array(self.xdocterm[:, token_indices].sum(axis=1)).squeeze() / norm
        return topic_vector

    def explain_topic_for_text(self, text: str, topic_title: str) -> pd.DataFrame:
        text_df = pd.DataFrame(self._tokenize(text), columns=["full_token"])
        text_df["token"] = self._stem_and_tokenize(text)
        topic_df = self.topn_tokens_from_topic(topic_title, topn=1000)
        explanation = pd.merge(text_df, topic_df, on="token")
        return explanation.sort_values("score", ascending=False)

    def topn_tokens_from_topic(self, topic_title: str, topn: int = 10) -> pd.DataFrame:
        indx = self.topic_df.index[self.topic_df["page_title"] == topic_title][0]
        token_vector = self.xdocterm.getrow(indx).toarray().squeeze()
        token_indxs = np.argsort(-token_vector)[:topn]
        tokens = pd.DataFrame(
            zip(self.indx2tok[token_indxs], token_vector[token_indxs]), columns=["token", "score"]
        )
        return tokens
