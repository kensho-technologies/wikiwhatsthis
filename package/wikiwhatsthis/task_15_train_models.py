# Copyright 2020-present Kensho Technologies, LLC.
import json
import logging
import os
import subprocess
from typing import Dict, Iterator

import joblib
import pandas as pd
import scipy.sparse
from sklearn.feature_extraction.text import CountVectorizer
from tqdm import tqdm

from bm25_transformer import BM25Transformer
from nltk.stem.snowball import SnowballStemmer

from wikiwhatsthis import argconfig

import warnings

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message="Your stop_words may be inconsistent with your preprocessing.",
)


logger = logging.getLogger(__name__)


def count_file_lines(file_path: str) -> int:
    output = subprocess.check_output(["wc", "-l", file_path])
    num_lines = int(output.split()[0])
    return num_lines


def dump(
    wwt_config: Dict,
    cv: CountVectorizer,
    df_articles: pd.DataFrame,
    xcv: scipy.sparse.csr_matrix,
    xbm25: scipy.sparse.csr_matrix,
    output_path: str = "",
) -> None:
    os.makedirs(output_path, exist_ok=True)

    file_name = os.path.join(output_path, "wwt_config.json")
    with open(file_name, "w") as fp:
        json.dump(wwt_config, fp, indent=4)

    cv.stop_words_ = set()
    file_name = os.path.join(output_path, "cv.joblib")
    joblib.dump(cv, file_name)

    file_name = os.path.join(output_path, "df_articles.csv")
    df_articles.to_csv(file_name, index=False)

    file_name = os.path.join(output_path, "xcv.npz")
    scipy.sparse.save_npz(file_name, xcv)

    file_name = os.path.join(output_path, "xbm25.npz")
    scipy.sparse.save_npz(file_name, xbm25)


class WwtCorpus:
    def __init__(self, corpus_path: str, article_path: str):
        self.corpus_path = corpus_path
        self.article_path = article_path
        self._num_lines = count_file_lines(article_path) - 1

    def __iter__(self) -> Iterator[Dict]:
        with open(self.corpus_path, "r") as fp:
            for line in tqdm(fp, total=self._num_lines, dynamic_ncols=True):
                yield json.loads(line)

    def iter_chunks(self, scope: str) -> Iterator[str]:
        if scope == "paragraph":
            for page in self:
                if page["paragraphs"]:
                    yield page["paragraphs"][0]["plaintext_snowball"]
                else:
                    yield ""
        elif scope == "intro":
            for page in self:
                if page["paragraphs"]:
                    yield " ".join(
                        [
                            para["plaintext_snowball"]
                            for para in page["paragraphs"]
                            if para["section_idx"] == 0
                        ]
                    )
                else:
                    yield ""
        elif scope == "page":
            for page in self:
                if page["paragraphs"]:
                    yield " ".join([para["plaintext_snowball"] for para in page["paragraphs"]])
                else:
                    yield ""
        else:
            raise ValueError("scope must be one of ['paragraph', 'intro', 'page']")


def main(
    wp_yyyymmdd: str,
    data_path: str = argconfig.DEFAULT_KWNLP_DATA_PATH,
) -> None:

    output_path = os.path.join("/data/wiki-whats-this", wp_yyyymmdd)

    stemmer = SnowballStemmer("english")
    stop_words = frozenset(
        [stemmer.stem(token) for token in json.load(open("english_stop_words.json", "r"))]
    )

    corpora_names = [
        "feat",
        "good",
        "mini",
        "small",
        "views5000",
        "inlinks40",
        "views500",
        "inlinks20",
        "views50",
        "inlinks10",
        "fidu",
        "base",
    ]

    scopes = [
        "intro",
        "page",
    ]

    ngram_ranges = [(1, 1)]

    corpus_paths = {
        corpus_name: os.path.join(
            data_path,
            f"wikipedia-derived-{wp_yyyymmdd}",
            "wiki-whats-this",
            f"link-annotated-text-{corpus_name}",
            f"kwnlp-enwiki-{wp_yyyymmdd}-link-annotated-text-{corpus_name}.jsonl",
        )
        for corpus_name in corpora_names
    }

    article_paths = {
        corpus_name: os.path.join(
            data_path,
            f"wikipedia-derived-{wp_yyyymmdd}",
            "wiki-whats-this",
            f"link-annotated-text-{corpus_name}",
            f"kwnlp-enwiki-{wp_yyyymmdd}-article-{corpus_name}.csv",
        )
        for corpus_name in corpora_names
    }

    for scope in scopes:
        print(f"working on scope {scope}")

        for corpus_name in corpora_names:
            print(f"working on corpus {corpus_name}")

            for ngram_range in ngram_ranges:

                corpus = WwtCorpus(corpus_paths[corpus_name], article_paths[corpus_name])
                df_articles = pd.read_csv(article_paths[corpus_name], keep_default_na=False)

                cv_args = {
                    "min_df": 3,
                    "max_df": 0.85,
                    "ngram_range": ngram_range,
                    "max_features": 500_000,
                    "token_pattern": r"(?u)\b[^\d\W]{2,25}\b",
                    "stop_words": list(stop_words),
                }

                wwt_config = {
                    "corpus_name": corpus_name,
                    "scope": scope,
                    "stemmer": "snowball",
                    "cv_args": cv_args,
                }

                cv = CountVectorizer(**cv_args)
                xcv = cv.fit_transform(corpus.iter_chunks(scope))
                bm25 = BM25Transformer()
                xbm25 = bm25.fit_transform(xcv)
                model_path = os.path.join(
                    output_path,
                    f"{corpus_name}-{scope}-ngram{ngram_range[0]}{ngram_range[1]}-snowball",
                )
                dump(wwt_config, cv, df_articles, xcv, xbm25, output_path=model_path)


if __name__ == "__main__":

    description = "train explicit topic models"
    arg_names = ["wp_yyyymmdd", "data_path", "loglevel"]
    parser = argconfig.get_argparser(description, arg_names)

    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    logger.info(f"args={args}")

    main(
        args.wp_yyyymmdd,
        data_path=args.data_path,
    )
