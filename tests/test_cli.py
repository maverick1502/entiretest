import csv
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
    assert args.csv is None


def test_build_parser_recursive_flag(tmp_path: Path) -> None:
    parser = build_parser()
    args = parser.parse_args([str(tmp_path), "--recursive"])

    assert args.recursive is True


def test_build_parser_csv_flag(tmp_path: Path) -> None:
    csv_path = tmp_path / "out.csv"
    parser = build_parser()
    args = parser.parse_args([str(tmp_path), "--csv", str(csv_path)])

    assert args.csv == csv_path


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


def test_main_with_csv_flag_writes_file_and_confirms(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    _touch(tmp_path / "Argo (2012).mkv")
    csv_path = tmp_path / "out.csv"

    exit_code = main([str(tmp_path), "--csv", str(csv_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert f"CSV-Datei geschrieben: {csv_path}" in captured.out
    assert csv_path.exists()

    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle, delimiter=";"))

    assert rows[0] == ["Pfad", "Dateiname", "Jahr", "Size"]
    assert rows[1][0] == str(tmp_path)
    assert rows[1][1] == "Argo"
    assert rows[1][2] == "2012"


def test_main_with_csv_flag_and_no_files_writes_header_only(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    csv_path = tmp_path / "out.csv"

    exit_code = main([str(tmp_path), "--csv", str(csv_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Keine .mkv-Dateien gefunden." in captured.out

    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle, delimiter=";"))

    assert rows == [["Pfad", "Dateiname", "Jahr", "Size"]]


def test_main_without_csv_flag_does_not_write_file(tmp_path: Path) -> None:
    _touch(tmp_path / "a.mkv")

    main([str(tmp_path)])

    assert list(tmp_path.glob("*.csv")) == []


def test_main_returns_error_when_csv_destination_is_invalid(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    _touch(tmp_path / "a.mkv")
    invalid_csv_path = tmp_path / "no_such_dir" / "out.csv"

    exit_code = main([str(tmp_path), "--csv", str(invalid_csv_path)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Fehler beim Schreiben der CSV-Datei" in captured.err


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
