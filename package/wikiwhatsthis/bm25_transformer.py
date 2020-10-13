# Copyright 2020-present Kensho Technologies, LLC.
"""Adapted from.

 * https://github.com/scikit-learn/scikit-learn/blob/master/sklearn/feature_extraction/text.py
 * https://github.com/arosh/BM25Transformer

Background
 * http://www.kmwllc.com/index.php/2020/03/20/understanding-tf-idf-and-bm25/
 * https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables
 * https://en.wikipedia.org/wiki/Okapi_BM25
"""
from typing import Any

import numpy as np
import scipy.sparse
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_is_fitted, check_array, FLOAT_DTYPES
from sklearn.utils.fixes import _astype_copy_false
from sklearn.feature_extraction.text import _document_frequency


class BM25Transformer(BaseEstimator, TransformerMixin):
    def __init__(self, use_idf: bool = True, k1: float = 1.2, b: float = 0.75):
        self.use_idf = use_idf
        self.k1 = k1
        self.b = b

    def fit(self, X: scipy.sparse.csr_matrix, y: Any = None) -> "BM25Transformer":
        """Learn the idf vector (global term weights).

        Parameters
        ----------
        X : sparse matrix of shape n_samples, n_features)
            A matrix of term/token counts.
        """
        X = check_array(X, accept_sparse=("csr", "csc"))
        if not scipy.sparse.issparse(X):
            X = scipy.sparse.csr_matrix(X)
        dtype = X.dtype if X.dtype in FLOAT_DTYPES else np.float64

        if self.use_idf:
            n_samples, n_features = X.shape
            df = _document_frequency(X)
            df = df.astype(dtype, **_astype_copy_false(df))

            idf = np.log(1 + (n_samples - df + 0.5) / (df + 0.5))
            self._idf_diag = scipy.sparse.diags(
                idf, offsets=0, shape=(n_features, n_features), format="csr", dtype=dtype
            )
        return self

    def transform(self, X: scipy.sparse.csr_matrix, copy: bool = True) -> scipy.sparse.csr_matrix:
        """Transform a count matrix to a tf or bm25 representation.

        Parameters
        ----------
        X : sparse matrix of (n_samples, n_features)
            a matrix of term/token counts
        copy : bool, default=True
            Whether to copy X and operate on the copy or perform in-place
            operations.

        Returns
        -------
        vectors : sparse matrix of shape (n_samples, n_features)
        """
        X = check_array(X, accept_sparse="csr", dtype=FLOAT_DTYPES, copy=copy)
        if not scipy.sparse.issparse(X):
            X = scipy.sparse.csr_matrix(X, dtype=np.float64)

        n_samples, n_features = X.shape

        # Document length (number of terms) in each row
        # Shape is (n_samples, 1)
        dl = X.sum(axis=1)
        # Number of non-zero elements in each row
        # Shape is (n_samples, )
        sz = X.indptr[1:] - X.indptr[:-1]
        # In each row, repeat `dl` for `sz` times
        # Shape is (sum(sz), )
        # Example
        # -------
        # dl = [4, 5, 6]
        # sz = [1, 2, 3]
        # rep = [4, 5, 5, 6, 6, 6]
        rep = np.repeat(np.asarray(dl), sz)
        # Mean document length
        # Scalar value
        avgdl = np.mean(dl)
        # Compute BM25 score only for non-zero elements
        data = X.data * (self.k1 + 1) / (X.data + self.k1 * (1 - self.b + self.b * rep / avgdl))
        X = scipy.sparse.csr_matrix((data, X.indices, X.indptr), shape=X.shape, dtype=np.float64)

        if self.use_idf:
            check_is_fitted(self, attributes=["_idf_diag"], msg="idf vector is not fitted")

            expected_n_features = self._idf_diag.shape[0]
            if n_features != expected_n_features:
                raise ValueError(
                    "Input has n_features=%d while the model"
                    " has been trained with n_features=%d" % (n_features, expected_n_features)
                )
            # *= doesn't work
            X = X * self._idf_diag

        return X
