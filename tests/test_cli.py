import io
import json
import re

from Strainer import clean, main


def test_main_outputs_json_with_compression(monkeypatch, capsys):
    text = (
        "This is a sufficiently long sentence to be captured in the summary output. "
        "Another informative sentence follows to give the summarizer more material."
    )
    monkeypatch.setattr("sys.stdin", io.StringIO(text))

    exit_code = main(["Strainer.py", "-"])
    captured = capsys.readouterr().out
    result = json.loads(captured)

    assert exit_code == 0
    assert result["summary"]
    assert isinstance(result["tags"], list) and result["tags"]
    assert result["metrics"]["original_words"] > 0
    assert result["metrics"]["summary_words"] > 0
    assert re.match(r"^[0-9]+(?:\.[0-9])?%$", result["metrics"]["compression"])


def test_main_missing_file_reports_error_json(tmp_path, capsys):
    missing_path = tmp_path / "missing.txt"

    exit_code = main(["Strainer.py", str(missing_path)])
    captured = capsys.readouterr().out
    result = json.loads(captured)

    assert exit_code == 1
    assert result["error"]
    assert str(missing_path) in result["error"]


def test_main_includes_anchors_with_flag(monkeypatch, capsys):
    text = "Alpha beta. Gamma delta."
    cleaned = clean(text)
    monkeypatch.setattr("sys.stdin", io.StringIO(text))

    exit_code = main(["Strainer.py", "-", "--include-anchors"])
    captured = capsys.readouterr().out
    result = json.loads(captured)

    assert exit_code == 0
    assert "evidence" in result
    assert result["evidence"]["summary"]
    first_anchor = result["evidence"]["summary"][0]
    assert cleaned[first_anchor["start"] : first_anchor["end"]] == first_anchor["sentence"]
    if "tags" in result["evidence"]:
        for entry in result["evidence"]["tags"]:
            position = entry["position"]
            if position is not None:
                assert cleaned[position : position + len(entry["tag"])].lower() == entry["tag"]


def test_main_respects_env_toggle(monkeypatch, capsys):
    text = "Env toggle sentence."
    monkeypatch.setenv("STRAINER_INCLUDE_ANCHORS", "1")
    monkeypatch.setattr("sys.stdin", io.StringIO(text))

    exit_code = main(["Strainer.py", "-"])
    captured = capsys.readouterr().out
    result = json.loads(captured)

    assert exit_code == 0
    assert "evidence" in result
    assert result["evidence"]["summary"]
