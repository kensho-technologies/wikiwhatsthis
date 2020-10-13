# Copyright 2020-present Kensho Technologies, LLC.
"""Add stemmed words to plaintext chunks and filter sections.

Can do all chunks at once with a machine with 64 cores and 256G RAM
"""
import json
import logging
from multiprocessing import Pool
import os
import re
from typing import Callable, Dict, List, Union

from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer

from wikiwhatsthis import argconfig
from wikiwhatsthis import patterns


logger = logging.getLogger(__name__)


FORBIDDEN_SECTIONS = frozenset(
    [
        "see also",  # citation-like
        "external links",  # citation-like
        "cast",  # list-like
        "references",  # citation-like
        "personnel",  # people-list-like
        "honours",  # list-like
        "awards",  # list-like
        "track listing",  # list-like
        "discography",  # list-like
        "further reading",  # citation-like
        "works",  # list-like
        "notable people",  # list-like
        "bibliography",  # citation-like
        "filmography",  # list-like
        "people",  # list-like
        "events",  # list-like
        "other uses",  # off-topic
        "music",  # list-like
        "places",  # list-like
        "notable alumni",  # list-like
        "sources",  # citation-like
        "deaths",  # list-like
        "publications",  # citation-like
        "births",  # list-like
        "selected filmography",  # citation-like
        "other",  # ?
        "awards and honors",  # list-like
        "characters",  # list-like
        "members",  # list-like
        "incumbents",  # list-like
        "honors",  # list-like
        "citations",  # citation-like
        "source",  # citation-like
        "participants",  # list-like
    ]
)


def filter_sections(page: Dict) -> Dict:
    page["paragraphs"] = [
        para
        for para in page["paragraphs"]
        if para["section_name"].strip().lower() not in FORBIDDEN_SECTIONS
    ]
    return page


def add_stems(page: Dict, stemmer: SnowballStemmer, tokenizer: Callable[[str], List[str]]) -> Dict:
    for paragraph in page["paragraphs"]:
        paragraph["plaintext_snowball"] = " ".join(
            [stemmer.stem(tok) for tok in tokenizer(paragraph["plaintext"])]
        )
    return page


def parse_file(args: Dict) -> None:

    stemmer = SnowballStemmer("english")
    cv = CountVectorizer()
    tokenizer = cv.build_tokenizer()
    out_file_name = os.path.basename(args["lat_file_path"])
    out_file_path = os.path.join(args["out_dump_paths"]["snbl"], out_file_name)
    logger.info("parsing {}".format(args["lat_file_path"]))
    with open(args["lat_file_path"], "r") as ifp, open(out_file_path, "w") as ofp:
        for line in ifp:
            page = json.loads(line)
            page = filter_sections(page)
            page = add_stems(page, stemmer, tokenizer)
            ofp.write("{}\n".format(json.dumps(page)))


def main(
    wp_yyyymmdd: str,
    data_path: str = argconfig.DEFAULT_KWNLP_DATA_PATH,
    workers: int = argconfig.DEFAULT_KWNLP_WORKERS,
) -> None:

    in_dump_paths = {
        "lat": os.path.join(
            data_path, f"wikipedia-derived-{wp_yyyymmdd}", "link-annotated-text-chunks"
        ),
    }

    out_dump_paths = {
        "snbl": os.path.join(
            data_path,
            f"wikipedia-derived-{wp_yyyymmdd}",
            "wiki-whats-this",
            f"link-annotated-text-snowball-chunks",
        ),
    }

    for name, path in in_dump_paths.items():
        logger.info(f"{name} path: {path}")

    for name, path in out_dump_paths.items():
        os.makedirs(path, exist_ok=True)
        logger.info(f"{name} path: {path}")

    all_matches: List[Union[re.Match, None]] = [
        re.match(patterns.ARTICLES_DUMP_PATTERN, filename)
        for filename in os.listdir(in_dump_paths["lat"])
    ]
    non_null_matches: List[re.Match] = [match for match in all_matches if match is not None]
    sorted_matches = sorted(non_null_matches, key=lambda x: int(x.groupdict()["pageno_start"]))
    sorted_file_names = [match.string for match in sorted_matches]

    mp_args = []
    for file_name in sorted_file_names:
        file_path = os.path.join(in_dump_paths["lat"], file_name)
        mp_args.append(
            {
                "wp_yyyymmdd": wp_yyyymmdd,
                "lat_file_path": file_path,
                "out_dump_paths": out_dump_paths,
            }
        )
    with Pool(workers) as p:
        p.map(parse_file, mp_args)


if __name__ == "__main__":

    description = "filter sections and stem tokens"
    arg_names = ["wp_yyyymmdd", "data_path", "workers", "loglevel"]
    parser = argconfig.get_argparser(description, arg_names)

    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    logger.info(f"args={args}")

    main(
        args.wp_yyyymmdd,
        data_path=args.data_path,
        workers=args.workers,
    )
