# Copyright 2020-present Kensho Technologies, LLC.
import requests


base_url = "https://en.wikipedia.org/w/api.php"
params = {
    "action": "query",
    "prop": "transcludedin",
    "format": "json",
    "tilimit": "max",
    "tinamespace": 0,
}

titles = [
    "Template:Conspiracy_theories",
    "Template:Pseudoscience",
]


triples = set()
for title in titles:
    res = requests.get(base_url, params={**params, **{"titles": title}})
    oo = res.json()
    pgid = next(iter(oo["query"]["pages"].keys()))
    pages = oo["query"]["pages"][pgid]["transcludedin"]
    new_triples = set([tuple(page.values()) for page in pages])
    triples = triples.union(new_triples)
    print(title, len(pages))
