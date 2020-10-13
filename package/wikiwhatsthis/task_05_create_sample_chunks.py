# Copyright 2020-present Kensho Technologies, LLC.
"""Create different samples from stemmed/section filtered chunks."""
import json
import logging
import os
import re
from typing import Dict, List, Union

import pandas as pd

from wikiwhatsthis import argconfig
from wikiwhatsthis import patterns


logger = logging.getLogger(__name__)


def create_sample(args: Dict) -> None:

    keep_page_ids = set(args["df_articles"]["page_id"].values)
    for match in args["lat_matches"]:
        mgd = match.groupdict()
        parsed_page_ids = []
        in_file_path = os.path.join(args["lat_file_path"], match.string)
        out_file_name = "kwnlp-{}-{}-link-annotated-text{}-{}-{}.jsonl".format(
            mgd["wiki"], mgd["wp_yyyymmdd"], mgd["fileno"], mgd["page_signature"], args["mask_name"]
        )
        out_file_path = os.path.join(args["out_file_path"], out_file_name)
        logger.info(f"writing {out_file_path}")
        with open(in_file_path, "r") as ifp, open(out_file_path, "w") as ofp:
            for line in ifp:
                page = json.loads(line)
                if page["page_id"] in keep_page_ids:
                    ofp.write(line)
                    parsed_page_ids.append(page["page_id"])

        # reorder df_articles to match order in link annotated text file
        df = args["df_articles"].set_index("page_id").loc[parsed_page_ids]
        assert df.shape[0] == len(parsed_page_ids)
        out_file_name = "kwnlp-{}-{}-article{}-{}-{}.csv".format(
            mgd["wiki"], mgd["wp_yyyymmdd"], mgd["fileno"], mgd["page_signature"], args["mask_name"]
        )
        out_file_path = os.path.join(args["out_file_path"], out_file_name)
        logger.info(f"writing {out_file_path}")
        df.to_csv(out_file_path)


def create_df_base_articles(df_articles: pd.DataFrame) -> pd.DataFrame:
    """Remove articles we never want to use."""
    # create filters for different subsets of articles
    # (mask indicates pages we want to keep)
    mask_17442446 = df_articles[f"isa_Q17442446"] == 0
    mask_14795564 = df_articles[f"isa_Q14795564"] == 0
    mask_18340514 = df_articles[f"isa_Q18340514"] == 0
    mask_wikidata = df_articles["item_id"] != -1

    # catch internal items that were missed by wikimedia internal item
    mask_list = ~df_articles["page_title"].str.lower().str.startswith("list_of_")
    mask_disa = ~df_articles["page_title"].str.lower().str.endswith("(disambiguation)")

    mask_base = (
        mask_17442446 & mask_14795564 & mask_18340514 & mask_wikidata & mask_list & mask_disa
    )
    return df_articles[mask_base].copy()


def main(
    wp_yyyymmdd: str,
    data_path: str = argconfig.DEFAULT_KWNLP_DATA_PATH,
    workers: int = argconfig.DEFAULT_KWNLP_WORKERS,
) -> None:

    # set data paths
    # ============================================================
    lat_file_path = os.path.join(
        data_path,
        f"wikipedia-derived-{wp_yyyymmdd}",
        "wiki-whats-this",
        "link-annotated-text-snowball-chunks",
    )

    art_file_path = os.path.join(
        data_path,
        f"wikipedia-derived-{wp_yyyymmdd}",
        "kwnlp-sql",
        f"kwnlp-enwiki-{wp_yyyymmdd}-article.csv",
    )

    wiki_whats_this_path = os.path.join(
        data_path,
        f"wikipedia-derived-{wp_yyyymmdd}",
        "wiki-whats-this",
    )

    # create list of input link annotated text files
    # ============================================================
    all_lat_matches: List[Union[re.Match, None]] = [
        re.match(patterns.ARTICLES_DUMP_PATTERN, filename) for filename in os.listdir(lat_file_path)
    ]
    non_null_lat_matches: List[re.Match] = [match for match in all_lat_matches if match is not None]
    sorted_lat_matches = sorted(
        non_null_lat_matches, key=lambda x: int(x.groupdict()["pageno_start"])
    )

    # create base articles
    # ============================================================
    logger.info("reading {}".format(art_file_path))
    df_articles = pd.read_csv(art_file_path, keep_default_na=False)

    logger.info("creating base article dataframe")
    df_base_articles = create_df_base_articles(df_articles)

    # create mp arguments for each mask
    # ============================================================
    mp_args = {}

    mask_base = df_base_articles["page_id"] == df_base_articles["page_id"]
    mask_feat = df_base_articles["tmpl_featured_article"] == 1
    mask_good = df_base_articles["tmpl_good_article"] == 1 | mask_feat

    mask_views50 = df_base_articles["views"] >= 50
    mask_views500 = df_base_articles["views"] >= 500
    mask_views5000 = df_base_articles["views"] >= 5000

    mask_inlinks10 = df_base_articles["in_link_count"] >= 10
    mask_inlinks20 = df_base_articles["in_link_count"] >= 20
    mask_inlinks40 = df_base_articles["in_link_count"] >= 40

    mask_fidu = mask_views50 & mask_inlinks10
    mask_small = mask_views500 & mask_inlinks20
    mask_mini = mask_views5000 & mask_inlinks40

    masks = {
        "feat": mask_feat,
        "base": mask_base,
        "good": mask_good,
        "views50": mask_views50,
        "views500": mask_views500,
        "views5000": mask_views5000,
        "inlinks10": mask_inlinks10,
        "inlinks20": mask_inlinks20,
        "inlinks40": mask_inlinks40,
        "fidu": mask_fidu,
        "small": mask_small,
        "mini": mask_mini,
    }

    # write all samples
    # ============================================================
    for mask_name, mask in masks.items():
        out_file_path = os.path.join(
            wiki_whats_this_path, f"link-annotated-text-{mask_name}-chunks"
        )
        os.makedirs(out_file_path, exist_ok=True)
        logger.info(f"creating path: {out_file_path}")
        mp_args[mask_name] = {
            "mask_name": mask_name,
            "df_articles": df_base_articles[mask].copy(),
            "lat_matches": sorted_lat_matches,
            "lat_file_path": lat_file_path,
            "art_file_path": art_file_path,
            "out_file_path": out_file_path,
        }
        create_sample(mp_args[mask_name])


#    sys.exit(1)
#    with Pool(workers) as p:
#        p.map(parse_file, mp_args)


if __name__ == "__main__":

    description = "create model samples"
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
