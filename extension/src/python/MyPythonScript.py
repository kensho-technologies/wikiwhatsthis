# Copyright 2020-present Kensho Technologies, LLC.
import io
from nltk.stem.snowball import SnowballStemmer
import scipy.sparse
import joblib
import pandas as pd
import numpy as np


global_objects = {
    "stemmer": SnowballStemmer("english"),
}


# Make loading safe vs. malicious input
PICKLE_KWARGS = dict(allow_pickle=False)


def load_npz(file):
    """Load a sparse matrix from a file using ``.npz`` format.
    Parameters
    ----------
    file : str or file-like object
        Either the file name (string) or an open file (file-like object)
        where the data will be loaded.
    Returns
    -------
    result : csc_matrix, csr_matrix, bsr_matrix, dia_matrix or coo_matrix
        A sparse matrix containing the loaded data.
    Raises
    ------
    IOError
        If the input file does not exist or cannot be read.
    See Also
    --------
    scipy.sparse.save_npz: Save a sparse matrix to a file using ``.npz`` format.
    numpy.load: Load several arrays from a ``.npz`` archive.
    Examples
    --------
    Store sparse matrix to disk, and load it again:
    >>> import scipy.sparse
    >>> sparse_matrix = scipy.sparse.csc_matrix(np.array([[0, 0, 3], [4, 0, 0]]))
    >>> sparse_matrix
    <2x3 sparse matrix of type '<class 'numpy.int64'>'
       with 2 stored elements in Compressed Sparse Column format>
    >>> sparse_matrix.todense()
    matrix([[0, 0, 3],
            [4, 0, 0]], dtype=int64)
    >>> scipy.sparse.save_npz('/tmp/sparse_matrix.npz', sparse_matrix)
    >>> sparse_matrix = scipy.sparse.load_npz('/tmp/sparse_matrix.npz')
    >>> sparse_matrix
    <2x3 sparse matrix of type '<class 'numpy.int64'>'
        with 2 stored elements in Compressed Sparse Column format>
    >>> sparse_matrix.todense()
    matrix([[0, 0, 3],
            [4, 0, 0]], dtype=int64)
    """

    with np.load(file, **PICKLE_KWARGS) as loaded:
        try:
            matrix_format = loaded["format"]
        except KeyError as e:
            raise ValueError("The file {} does not contain a sparse matrix.".format(file)) from e

        matrix_format = matrix_format.item()

        if not isinstance(matrix_format, str):
            # Play safe with Python 2 vs 3 backward compatibility;
            # files saved with SciPy < 1.0.0 may contain unicode or bytes.
            matrix_format = matrix_format.decode("ascii")

        try:
            cls = getattr(scipy.sparse, "{}_matrix".format(matrix_format))
        except AttributeError as e:
            raise ValueError('Unknown matrix format "{}"'.format(matrix_format)) from e

        if matrix_format in ("csc", "csr", "bsr"):
            return cls((loaded["data"], loaded["indices"], loaded["indptr"]), shape=loaded["shape"])
        elif matrix_format == "dia":
            return cls((loaded["data"], loaded["offsets"]), shape=loaded["shape"])
        elif matrix_format == "coo":
            return cls((loaded["data"], (loaded["row"], loaded["col"])), shape=loaded["shape"])
        else:
            raise NotImplementedError(
                "Load is not implemented for " "sparse matrix of format {}.".format(matrix_format)
            )


def set_model_file_data(name, value):
    if name == "df_articles.csv":
        print("reading {}".format(name))
        # print("type(value): ", type(value))
        global_objects["df_articles"] = pd.read_csv(io.BytesIO(value))
        # print(global_objects["df_articles"].head())

    if name == "cv.joblib":
        print("reading {}".format(name))
        # print("type(value): ", type(value))
        global_objects["cv"] = joblib.load(io.BytesIO(value))
        global_objects["tokenizer"] = global_objects["cv"].build_tokenizer()
        global_objects["analyzer"] = global_objects["cv"].build_analyzer()
        # print(global_objects["cv"])

    if name == "xbm25.npz":
        print("reading {}".format(name))
        # print("type(value): ", type(value))
        global_objects["xbm25"] = load_npz(io.BytesIO(value))
        # print(global_objects["xbm25"][0])


def search(text):

    topn = 10
    thresh = 0.0

    # print("input text: ", text)

    raw_tokens = global_objects["tokenizer"](text)
    # print("raw tokens: ", raw_tokens)

    stemmed_tokens = [global_objects["stemmer"].stem(tok) for tok in raw_tokens]
    # print("stemmed tokens: ", stemmed_tokens)

    stemmed_text = " ".join(stemmed_tokens)
    # print("stemmed text: ", stemmed_text)

    tokens = global_objects["analyzer"](stemmed_text)
    # print("tokens: ", tokens)

    token_indices = [
        global_objects["cv"].vocabulary_[token]
        for token in tokens
        if token in global_objects["cv"].vocabulary_
    ]
    # print("token_indices: ", token_indices)

    norm = max(1, len(token_indices))
    topic_vector = np.array(global_objects["xbm25"][:, token_indices].sum(axis=1)).squeeze() / norm
    # print("topic_vector: ", topic_vector)

    topic_indxs = np.argsort(-topic_vector)[:topn]
    top_topics_df = global_objects["df_articles"].iloc[topic_indxs].copy()
    topic_scores = topic_vector[topic_indxs]
    top_topics_df["score"] = topic_scores
    top_topics_df = top_topics_df[top_topics_df["score"] > thresh]
    # print("top_topics_df ... ")
    # for indx, row in top_topics_df.iterrows():
    #     print(row)

    return top_topics_df.to_json(orient="records")
