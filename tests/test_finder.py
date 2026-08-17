from pathlib import Path

import pytest

from mkv_lister.finder import find_mkv_files


def _touch(path: Path) -> None:
    path.write_text("dummy")


def test_raises_when_directory_does_not_exist(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist"

    with pytest.raises(FileNotFoundError, match="existiert nicht"):
        find_mkv_files(missing)


def test_raises_when_path_is_not_a_directory(tmp_path: Path) -> None:
    file_path = tmp_path / "not_a_dir.txt"
    _touch(file_path)

    with pytest.raises(NotADirectoryError, match="ist kein Ordner"):
        find_mkv_files(file_path)


def test_returns_empty_list_for_empty_directory(tmp_path: Path) -> None:
    assert find_mkv_files(tmp_path) == []


def test_finds_only_mkv_files_case_insensitive(tmp_path: Path) -> None:
    _touch(tmp_path / "movie1.mkv")
    _touch(tmp_path / "movie2.MKV")
    _touch(tmp_path / "movie3.mp4")
    _touch(tmp_path / "readme.txt")

    result = find_mkv_files(tmp_path)

    assert result == sorted(
        [tmp_path / "movie1.mkv", tmp_path / "movie2.MKV"],
        key=lambda p: str(p).lower(),
    )


def test_non_recursive_ignores_subdirectories(tmp_path: Path) -> None:
    _touch(tmp_path / "top.mkv")
    subdir = tmp_path / "sub"
    subdir.mkdir()
    _touch(subdir / "nested.mkv")

    result = find_mkv_files(tmp_path, recursive=False)

    assert result == [tmp_path / "top.mkv"]


def test_recursive_finds_nested_files(tmp_path: Path) -> None:
    _touch(tmp_path / "top.mkv")
    subdir = tmp_path / "sub"
    subdir.mkdir()
    _touch(subdir / "nested.mkv")
    deeper = subdir / "deeper"
    deeper.mkdir()
    _touch(deeper / "deepest.mkv")

    result = find_mkv_files(tmp_path, recursive=True)

    assert result == sorted(
        [tmp_path / "top.mkv", subdir / "nested.mkv", deeper / "deepest.mkv"],
        key=lambda p: str(p).lower(),
    )


def test_directory_named_like_mkv_file_is_not_included(tmp_path: Path) -> None:
    fake_dir = tmp_path / "looks_like_a_file.mkv"
    fake_dir.mkdir()
    _touch(fake_dir / "inside.mkv")

    non_recursive = find_mkv_files(tmp_path, recursive=False)
    recursive = find_mkv_files(tmp_path, recursive=True)

    assert non_recursive == []
    assert recursive == [fake_dir / "inside.mkv"]


def test_accepts_string_path(tmp_path: Path) -> None:
    _touch(tmp_path / "movie.mkv")

    result = find_mkv_files(str(tmp_path))

    assert result == [tmp_path / "movie.mkv"]


def test_result_is_sorted_alphabetically(tmp_path: Path) -> None:
    _touch(tmp_path / "c.mkv")
    _touch(tmp_path / "a.mkv")
    _touch(tmp_path / "b.mkv")

    result = find_mkv_files(tmp_path)

    assert [p.name for p in result] == ["a.mkv", "b.mkv", "c.mkv"]
