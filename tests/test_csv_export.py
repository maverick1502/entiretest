import csv
from pathlib import Path

from mkv_lister.csv_export import CSV_HEADER, format_size, parse_filename, write_csv


def _touch_with_size(path: Path, size: int) -> None:
    path.write_bytes(b"0" * size)


def test_parse_filename_with_year_at_end() -> None:
    assert parse_filename("Argo (2012)") == ("Argo", "2012")


def test_parse_filename_without_year() -> None:
    assert parse_filename("Documentary") == ("Documentary", "")


def test_parse_filename_with_year_in_middle() -> None:
    assert parse_filename("Movie (2012) Extended") == ("Movie Extended", "2012")


def test_parse_filename_ignores_non_year_parentheses() -> None:
    assert parse_filename("Movie (Director's Cut)") == ("Movie (Director's Cut)", "")


def test_parse_filename_strips_surrounding_whitespace() -> None:
    assert parse_filename("  Argo (2012)  ") == ("Argo", "2012")


def test_format_size_zero_bytes() -> None:
    assert format_size(0) == "0 B"


def test_format_size_plain_bytes() -> None:
    assert format_size(500) == "500 B"


def test_format_size_kilobytes() -> None:
    assert format_size(2048) == "2.00 KB"


def test_format_size_megabytes() -> None:
    assert format_size(5 * 1024 * 1024) == "5.00 MB"


def test_format_size_gigabytes() -> None:
    assert format_size(int(1.5 * 1024 ** 3)) == "1.50 GB"


def test_format_size_beyond_petabytes_falls_back_to_exabytes() -> None:
    assert format_size(2 * 1024 ** 6) == "2.00 EB"


def test_write_csv_creates_header_and_rows(tmp_path: Path) -> None:
    movie_dir = tmp_path / "Filme" / "Argo"
    movie_dir.mkdir(parents=True)
    movie_file = movie_dir / "Argo (2012).mkv"
    _touch_with_size(movie_file, 1024)

    csv_path = tmp_path / "out.csv"
    write_csv([movie_file], csv_path)

    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle, delimiter=";"))

    assert rows[0] == CSV_HEADER
    assert rows[1] == [str(movie_dir), "Argo", "2012", "1.00 KB"]


def test_write_csv_without_year(tmp_path: Path) -> None:
    doc_file = tmp_path / "Documentary.mkv"
    _touch_with_size(doc_file, 10)

    csv_path = tmp_path / "out.csv"
    write_csv([doc_file], csv_path)

    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle, delimiter=";"))

    assert rows[1] == [str(tmp_path), "Documentary", "", "10 B"]


def test_write_csv_empty_list_writes_only_header(tmp_path: Path) -> None:
    csv_path = tmp_path / "out.csv"
    write_csv([], csv_path)

    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle, delimiter=";"))

    assert rows == [CSV_HEADER]


def test_write_csv_uses_utf8_encoding(tmp_path: Path) -> None:
    movie_file = tmp_path / "Über den Wolken (2005).mkv"
    _touch_with_size(movie_file, 1)

    csv_path = tmp_path / "out.csv"
    write_csv([movie_file], csv_path)

    content = csv_path.read_bytes().decode("utf-8")
    assert "Über den Wolken" in content
