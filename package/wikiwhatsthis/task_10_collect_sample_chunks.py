# Copyright 2020-present Kensho Technologies, LLC.
"""Collect chunks."""
import logging
import os
import re
from typing import List, Union

import pandas as pd

from wikiwhatsthis import argconfig
from wikiwhatsthis import patterns


logger = logging.getLogger(__name__)


SAMPLE_NAMES = [
    "feat",
    "good",
    "base",
    "fidu",
    "small",
    "mini",
    "inlinks10",
    "inlinks20",
    "inlinks40",
    "views50",
    "views500",
    "views5000",
]


def main(
    wp_yyyymmdd: str,
    data_path: str = argconfig.DEFAULT_KWNLP_DATA_PATH,
) -> None:

    in_dump_paths = {
        key: os.path.join(
            data_path,
            f"wikipedia-derived-{wp_yyyymmdd}",
            "wiki-whats-this",
            f"link-annotated-text-{key}-chunks",
        )
        for key in SAMPLE_NAMES
    }

    out_dump_paths = {
        key: os.path.join(
            data_path,
            f"wikipedia-derived-{wp_yyyymmdd}",
            "wiki-whats-this",
            f"link-annotated-text-{key}",
        )
        for key in SAMPLE_NAMES
    }

    for key, path in in_dump_paths.items():
        logger.info(f"{key} path: {path}")

    for key, path in out_dump_paths.items():
        os.makedirs(path, exist_ok=True)
        logger.info(f"{key} path: {path}")

    for key in SAMPLE_NAMES:

        logger.info(f"working on {key}")

        all_lat_matches: List[Union[re.Match, None]] = [
            re.match(patterns.ARTICLES_DUMP_PATTERN, filename)
            for filename in os.listdir(in_dump_paths[key])
            if filename.endswith(".jsonl")
        ]
        non_null_lat_matches: List[re.Match] = [
            match for match in all_lat_matches if match is not None
        ]
        sorted_lat_matches = sorted(
            non_null_lat_matches, key=lambda x: int(x.groupdict()["pageno_start"])
        )

        out_file_name = "kwnlp-{}-{}-{}-{}.jsonl".format(
            "enwiki", wp_yyyymmdd, "link-annotated-text", key
        )
        out_file_path = os.path.join(out_dump_paths[key], out_file_name)
        with open(out_file_path, "w") as ofp:
            for match in sorted_lat_matches:
                in_file_name = match.string
                in_file_path = os.path.join(in_dump_paths[key], in_file_name)
                with open(in_file_path, "r") as ifp:
                    for line in ifp:
                        ofp.write(line)

        all_art_matches: List[Union[re.Match, None]] = [
            re.match(patterns.ARTICLES_DUMP_PATTERN, filename)
            for filename in os.listdir(in_dump_paths[key])
            if filename.endswith(".csv")
        ]
        non_null_art_matches: List[re.Match] = [
            match for match in all_art_matches if match is not None
        ]
        sorted_art_matches = sorted(
            non_null_art_matches, key=lambda x: int(x.groupdict()["pageno_start"])
        )

        out_file_name = "kwnlp-{}-{}-{}-{}.csv".format("enwiki", wp_yyyymmdd, "article", key)
        out_file_path = os.path.join(out_dump_paths[key], out_file_name)

        if os.path.exists(out_file_path):
            os.remove(out_file_path)
        write_header = True
        for match in sorted_art_matches:
            in_file_name = match.string
            in_file_path = os.path.join(in_dump_paths[key], in_file_name)
            df = pd.read_csv(in_file_path, keep_default_na=False)
            df.to_csv(out_file_path, mode="a", header=write_header, index=False)
            if write_header:
                write_header = False


if __name__ == "__main__":

    description = "gather sample chunks"
    arg_names = ["wp_yyyymmdd", "data_path", "loglevel"]
    parser = argconfig.get_argparser(description, arg_names)

    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    logger.info(f"args={args}")

    main(
        args.wp_yyyymmdd,
        data_path=args.data_path,
    )
