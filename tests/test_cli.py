import io
import json
import re

from strainer.core import clean
from strainer.cli import main


def test_main_human_output_is_default(monkeypatch, capsys):
    """Default output should be human-readable, not JSON."""
    text = (
        "This is a sufficiently long sentence to be captured in the summary output. "
        "Another informative sentence follows to give the summarizer more material."
    )
    monkeypatch.setattr("sys.stdin", io.StringIO(text))

    exit_code = main(["strainer", "-"])
    captured = capsys.readouterr().out

    assert exit_code == 0
    # Human output has section headers
    assert "Summary" in captured
    assert "Tags" in captured
    assert "Stats" in captured
    # Should NOT be valid JSON
    try:
        json.loads(captured)
        assert False, "Default output should not be JSON"
    except json.JSONDecodeError:
        pass


def test_main_json_flag_outputs_json(monkeypatch, capsys):
    text = (
        "This is a sufficiently long sentence to be captured in the summary output. "
        "Another informative sentence follows to give the summarizer more material."
    )
    monkeypatch.setattr("sys.stdin", io.StringIO(text))

    exit_code = main(["strainer", "-", "--json"])
    captured = capsys.readouterr().out
    result = json.loads(captured)

    assert exit_code == 0
    assert result["summary"]
    assert isinstance(result["tags"], list) and result["tags"]
    assert result["metrics"]["original_words"] > 0
    assert result["metrics"]["summary_words"] > 0
    assert re.match(r"^[0-9]+(?:\.[0-9])?%$", result["metrics"]["compression"])


def test_main_missing_file_reports_error(tmp_path, capsys):
    missing_path = tmp_path / "missing.txt"

    exit_code = main(["strainer", str(missing_path)])
    captured = capsys.readouterr().err

    assert exit_code == 1
    assert str(missing_path) in captured


def test_main_missing_file_json_mode(tmp_path, capsys):
    missing_path = tmp_path / "missing.txt"

    exit_code = main(["strainer", str(missing_path), "--json"])
    captured = capsys.readouterr().out
    result = json.loads(captured)

    assert exit_code == 1
    assert result["error"]
    assert str(missing_path) in result["error"]


def test_main_includes_anchors_with_flag(monkeypatch, capsys):
    text = "Alpha beta. Gamma delta."
    cleaned = clean(text)
    monkeypatch.setattr("sys.stdin", io.StringIO(text))

    exit_code = main(["strainer", "-", "--include-anchors", "--json"])
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

    exit_code = main(["strainer", "-", "--json"])
    captured = capsys.readouterr().out
    result = json.loads(captured)

    assert exit_code == 0
    assert "evidence" in result
    assert result["evidence"]["summary"]


def test_main_help_flag(capsys):
    exit_code = main(["strainer", "--help"])
    captured = capsys.readouterr().out

    assert exit_code == 0
    assert "strainer" in captured.lower()
    assert "--json" in captured


def test_main_version_flag(capsys):
    exit_code = main(["strainer", "--version"])
    captured = capsys.readouterr().out

    assert exit_code == 0
    assert "strainer" in captured.lower()


def test_main_no_args_shows_usage(capsys):
    exit_code = main(["strainer"])
    captured = capsys.readouterr().err

    assert exit_code == 1
    assert "Usage" in captured
