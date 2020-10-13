# Copyright 2020-present Kensho Technologies, LLC.
import re


CSV_DUMP_PATTERN = re.compile(
    r"""
        kwnlp            # literal "kwnlp"
        -                # literal "-"
    (?P<wiki>
    (?P<lang>
        [^\W\d]+         # wiki language code (e.g. "en")
    )
        wiki             # literal "wiki"
    )
    -                    # literal "-"
    (?P<wp_yyyymmdd>
        \d{8}            # yyyymmdd
    )
    -                    # literal "-"
    (?P<content>
        [-\w]+           # content description (e.g. "pages-articles")
    )
    \.                   # literal "."
    (?P<extension>
        \w+              # extension (e.g. "csv")
    )
    """,
    re.VERBOSE,
)

ARTICLES_DUMP_PATTERN = re.compile(
    r"""
        (kwnlp-)?        # optional initial "kwnlp-"
    (?P<wiki>
    (?P<lang>
        [^\W\d]+         # wiki language code (e.g. "en")
    )
        wiki             # literal "wiki"
    )
    -                    # literal "-"
    (?P<wp_yyyymmdd>
        \d{8}            # yyyymmdd
    )
    -                    # literal "-"
    (?P<content>
        ([-]|[^\W\d])+   # content description (e.g. "pages-articles")
    )
    (?P<fileno>
        \d{1,2}          # file number (not unique)
    )
    (
    \.                   # literal "."
    (?P<mid_extension>
        [^\W\d]+         # format extension (e.g. "xml")
    )
    )?
    -
    (?P<page_signature>
    (?P<page_start>
        p                # literal "p"
    (?P<pageno_start>
        \d+              # page number start
    ))
    (?P<page_end>
        p                # literal "p"
    (?P<pageno_end>
        \d+              # page number end
    ))
    )
        -?               # optional literal "-"
    (?P<subsample_name>
        \w+              # optional subsample name
    )?
    \.                   # literal "."
    (?P<extension>
        \w+              # extension (e.g. "bz2")
    )
    """,
    re.VERBOSE,
)

if __name__ == "__main__":
    file_name = "enwiki-20200920-pages-articles19.xml-p28621851p30121850.bz2"
    match = re.match(ARTICLES_DUMP_PATTERN, file_name)
    if match is not None:
        print(match.groupdict())

    file_name = "kwnlp-enwiki-20200920-link-annotated-text13-p10672789p11659682.jsonl"
    match = re.match(ARTICLES_DUMP_PATTERN, file_name)
    if match is not None:
        print(match.groupdict())

    file_name = "kwnlp-enwiki-20200920-prior-month-pagecounts-views-ge-5-totals.csv"
    match = re.match(CSV_DUMP_PATTERN, file_name)
    if match is not None:
        print(match.groupdict())
