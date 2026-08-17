import subprocess
import sys
from pathlib import Path

import pytest

from mkv_lister.cli import build_parser, main


def _touch(path: Path) -> None:
    path.write_text("dummy")


def test_build_parser_defaults(tmp_path: Path) -> None:
    parser = build_parser()
    args = parser.parse_args([str(tmp_path)])

    assert args.directory == tmp_path
    assert args.recursive is False


def test_build_parser_recursive_flag(tmp_path: Path) -> None:
    parser = build_parser()
    args = parser.parse_args([str(tmp_path), "--recursive"])

    assert args.recursive is True


def test_main_prints_found_files(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    _touch(tmp_path / "a.mkv")
    _touch(tmp_path / "b.mkv")

    exit_code = main([str(tmp_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert str(tmp_path / "a.mkv") in captured.out
    assert str(tmp_path / "b.mkv") in captured.out


def test_main_prints_message_when_no_files_found(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    exit_code = main([str(tmp_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Keine .mkv-Dateien gefunden." in captured.out


def test_main_returns_error_for_missing_directory(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    missing = tmp_path / "missing"

    exit_code = main([str(missing)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Fehler:" in captured.err
    assert "existiert nicht" in captured.err


def test_main_returns_error_when_path_is_a_file(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    file_path = tmp_path / "file.txt"
    _touch(file_path)

    exit_code = main([str(file_path)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "ist kein Ordner" in captured.err


def test_main_recursive_flag_finds_nested_files(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    subdir = tmp_path / "sub"
    subdir.mkdir()
    _touch(subdir / "nested.mkv")

    exit_code = main([str(tmp_path), "--recursive"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert str(subdir / "nested.mkv") in captured.out


def test_main_uses_sys_argv_when_argv_is_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    _touch(tmp_path / "a.mkv")
    monkeypatch.setattr(sys, "argv", ["mkv-lister", str(tmp_path)])

    exit_code = main()
    captured = capsys.readouterr()

    assert exit_code == 0
    assert str(tmp_path / "a.mkv") in captured.out


def test_cli_runs_as_module(tmp_path: Path) -> None:
    _touch(tmp_path / "a.mkv")
    repo_root = Path(__file__).resolve().parent.parent

    result = subprocess.run(
        [sys.executable, "-m", "mkv_lister.cli", str(tmp_path)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert str(tmp_path / "a.mkv") in result.stdout
