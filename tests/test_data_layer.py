import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import analytics as an
import data_loader as dl


MOVIES = """budget,genres,id,keywords,original_language,original_title,overview,popularity,production_companies,production_countries,release_date,revenue,runtime,title,vote_average,vote_count
100,"[{""id"": 1, ""name"": ""Drama""}, {""id"": 2, ""name"": ""Action""}]",1,[],en,A,Plot,10.5,[],[],2000-05-01,300,100,Alpha,8.0,1000
0,"[{""id"": 1, ""name"": ""Drama""}]",2,[],fr,B,,5.0,[],[],,0,,Beta,0,0
50,this is not json,3,[],en,C,Plot,1.0,[],[],1999-01-01,0,90,Gamma,6.0,10
"""
CREDITS = """movie_id,title,cast,crew
1,Alpha,"[{""name"": ""Ann""}]","[{""job"": ""Director"", ""name"": ""Dee""}]"
2,Beta,[],[]
"""


@pytest.fixture
def tiny(tmp_path):
    (tmp_path / "m.csv").write_text(MOVIES)
    (tmp_path / "c.csv").write_text(CREDITS)
    return dl.load_dataset(tmp_path / "m.csv", tmp_path / "c.csv")


# ---- data layer ----
def test_join_and_row_count(tiny):
    assert len(tiny) == 3 and tiny.loc[tiny.id == 1, "director"].iloc[0] == "Dee"


def test_json_parsing_and_malformed(tiny):
    assert tiny.loc[tiny.id == 1, "genres_list"].iloc[0] == ["Drama", "Action"]
    assert tiny.loc[tiny.id == 3, "genres_list"].iloc[0] == []          # malformed -> empty
    assert dl.parse_json_list("not json") == [] and dl.parse_json_list(None) == []


def test_missing_values_not_zero(tiny):
    b = tiny[tiny.id == 2].iloc[0]
    assert b["budget"] != b["budget"] and b["vote_average"] != b["vote_average"]   # NaN
    assert b["year"] != b["year"]                                                  # missing date


def test_year_extraction(tiny):
    assert tiny.loc[tiny.id == 1, "year"].iloc[0] == 2000


def test_missing_file_and_columns(tmp_path):
    with pytest.raises(dl.DatasetError, match="not found"):
        dl.load_dataset(tmp_path / "nope.csv", tmp_path / "nope2.csv")
    (tmp_path / "bad.csv").write_text("a,b\n1,2\n")
    with pytest.raises(dl.DatasetError, match="missing required columns"):
        dl.load_dataset(tmp_path / "bad.csv", tmp_path / "bad.csv")


# ---- analytics ----
def test_kpis(tiny):
    s = an.summary(tiny)
    assert s["total_movies"] == 3 and s["average_rating"] == 7.0       # unrated Beta excluded
    assert s["total_revenue"] == 300 and s["total_genres"] == 2


def test_genre_multi_count(tiny):
    d = {g["genre"]: g["count"] for g in an.genre_stats(tiny)}
    assert d == {"Drama": 2, "Action": 1}


def test_filter_sort_paginate(tiny):
    assert [m["title"] for m in an.paginate(an.filter_movies(tiny, q="ALP"), 0, 10)["items"]] == ["Alpha"]
    assert len(an.filter_movies(tiny, genre="drama")) == 2
    assert len(an.filter_movies(tiny, year_from=2000)) == 1
    assert len(an.filter_movies(tiny, min_rating=7)) == 1
    assert an.filter_movies(tiny, sort="rating").iloc[0]["title"] == "Alpha"
    assert an.paginate(tiny, 1, 1)["items"][0]["id"] and an.paginate(tiny, 5, 1)["items"] == []


def test_top_rated_min_votes(tiny):
    assert list(an.top_rated(tiny, min_votes=500)["title"]) == ["Alpha"]


