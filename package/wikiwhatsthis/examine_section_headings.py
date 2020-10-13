# Copyright 2020-present Kensho Technologies, LLC.
import os
import pandas as pd


FORBIDDEN_SECTIONS = frozenset(
    [
        "see also",
        "external links",
        "cast",  # people-list-like
        "references",
        "personnel",  # people-list-like
        "honours",  # list-like
        "awards",  # list-like
        "track listing",  # list-like
        "discography",  # list-like
        "further reading",
        "works",  # list-like
        "notable people",  # people-list-like
        "bibliography",
        "filmography",  # list-like
        "people",  # list-like
        "events",  # list-like
        "other uses",
        "music",  # list-like
        "places",  # list-like
        "notable alumni",  # list-like
        "sources",
        "deaths",
        "publications",
        "births",
        "selected filmography",
        "other",  # ?
        "awards and honors",
        "characters",
        "members",
        "incumbents",
        "honors",
        "citations",
        "source",
        "participants",
    ]
)


data_path = "/data/wikimedia-ingestion"
file_path = os.path.join(
    data_path,
    "wikipedia-derived-20200701",
    "section-names",
    "kwnlp-enwiki-20200701-section-names.csv",
)
df = pd.read_csv(file_path)


df["lwr_section_name"] = df["section_name"].str.strip().str.lower()

name_freq = df.groupby("lwr_section_name").size().sort_values(ascending=False)
df_name_freq = name_freq.to_frame().reset_index().rename(columns={0: "count"})
df_name_freq[df_name_freq["count"] > 5].to_csv("section_name_freq.csv", index=False)
