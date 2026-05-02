from pathlib import Path

_IMAGE_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg"})


def find_image(folder: Path, *, label: str) -> Path:
    images = [
        f
        for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in _IMAGE_EXTENSIONS
    ]
    if not images:
        msg = f"{label}에 사진 파일이 없습니다: {folder}"
        raise FileNotFoundError(msg)
    return images[0]
