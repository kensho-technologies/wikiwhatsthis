# Copyright 2020-present Kensho Technologies, LLC.
import os

import joblib
import numpy as np
import pandas as pd
import scipy.sparse
from sklearn.preprocessing import normalize

from explicit_topic_model import ExplicitTopicModel
from nltk.stem.snowball import SnowballStemmer


def explain_row(xdocterm, row_indx, row_labels, col_labels):
    row = xdocterm.getrow(row_indx).toarray().flatten()
    num_finite_entries = (row > 0).sum()
    col_indxs = np.argsort(-row)[:num_finite_entries]
    return zip(col_indxs, col_labels[col_indxs], row[col_indxs])


def explain_col(xdocterm, col_indx, row_labels, col_labels):
    col = xdocterm.getcol(col_indx).toarray().flatten()
    num_finite_entries = (col > 0).sum()
    row_indxs = np.argsort(-col)[:num_finite_entries]
    return zip(row_indxs, row_labels[row_indxs], col[row_indxs])


if __name__ == "__main__":

    data_path = "/data/wiki-whats-this"
    wp_yyyymmdd = "20200920"
    corpora_names = [
        "feat",
        "good",
        "base",
        "fidu",
        "views5",
        "views50",
        "views500",
        "inlinks10",
        "inlinks20",
        "inlinks40",
    ]

    scopes = [
        "paragraph",
        "intro",
        "page",
    ]

    corpus_name = "inlinks10"
    #    corpus_name = "fidu"
    #    corpus_name = "base"
    scope = "intro"

    model_path = os.path.join(data_path, wp_yyyymmdd, f"{corpus_name}-{scope}-ngram11-snowball")

    #    file_path = os.path.join(model_path, "xcv.npz")
    #    xcv = scipy.sparse.load_npz(file_path)

    file_path = os.path.join(model_path, "xbm25.npz")
    xbm25 = scipy.sparse.load_npz(file_path)

    file_path = os.path.join(model_path, "cv.joblib")
    cv = joblib.load(file_path)

    file_path = os.path.join(model_path, "df_articles.csv")
    df_articles = pd.read_csv(file_path, keep_default_na=False)

    stemmer = SnowballStemmer("english")
    etm_norm_term_vecs = ExplicitTopicModel(cv, normalize(xbm25, axis=0), df_articles, stemmer)
    etm_norm_docs_vecs = ExplicitTopicModel(cv, normalize(xbm25, axis=1), df_articles, stemmer)

    row_labels = df_articles["page_title"].values
    col_labels = np.array(cv.get_feature_names())

    text1 = """
    The canine - which was two months old when it died - has been
    remarkably preserved in the permafrost of the Russian region, with its
    fur, nose and teeth all intact.  DNA sequencing has been unable to determine
    the species.  Scientists say that could mean the specimen represents an
    evolutionary link between wolves and modern dogs.
    """

    text2 = """
    U.S. intelligence cannot say conclusively that Saddam Hussein
    has weapons of mass destruction, an information gap that is complicating
    White House efforts to build support for an attack on Saddam's Iraqi regime.
    The CIA has advised top administration officials to assume that Iraq has
    some weapons of mass destruction.  But the agency has not given President
    Bush a "smoking gun," according to U.S. intelligence and administration
    officials.
    """

    text3 = """
    The development of T-cell leukaemia following the otherwise
    successful treatment of three patients with X-linked severe combined
    immune deficiency (X-SCID) in gene-therapy trials using haematopoietic
    stem cells has led to a re-evaluation of this approach.  Using a mouse
    model for gene therapy of X-SCID, we find that the corrective therapeutic
    gene IL2RG itself can act as a contributor to the genesis of T-cell
    lymphomas, with one-third of animals being affected.  Gene-therapy trials
    for X-SCID, which have been based on the assumption that IL2RG is minimally
    oncogenic, may therefore pose some risk to patients.
    """

    text4 = """
    Share markets in the US plummeted on Wednesday, with losses accelerating
    after the World Health Organization declared the coronavirus outbreak a pandemic.
    """
