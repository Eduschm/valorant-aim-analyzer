"""Gate tests for the model-absent warning path — no model file required."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import services.cv.main as cv_main


def test_check_model_prints_warning_when_absent(capsys, tmp_path):
    """_check_model() writes an actionable message to stderr when the model is missing."""
    cv_main._check_model(str(tmp_path / "nonexistent.pt"))
    captured = capsys.readouterr()
    assert "download_model.py" in captured.err
    assert "WARNING" in captured.err


def test_check_model_silent_when_model_present(capsys, tmp_path):
    """_check_model() produces no output when the model file exists."""
    model_file = tmp_path / "valorant.pt"
    model_file.write_bytes(b"fake weights")
    cv_main._check_model(str(model_file))
    captured = capsys.readouterr()
    assert captured.err == ""


def test_download_model_script_exists():
    """The download script is present at the documented path."""
    script = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "download_model.py"
    )
    assert os.path.exists(os.path.abspath(script)), (
        "services/cv/scripts/download_model.py not found"
    )
