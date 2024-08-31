from pathlib import Path
from typing import Optional


IMAGE_EXT = [".jpeg", ".jpg", ".png", ".heic"]
VIDEO_EXT = [".mov", ".mp4"]


def load_dir(
    path: str | Path,
    *,
    recursive: bool = False,
    include_images: bool = True,
    include_videos: bool = True,
    allowed_ext: Optional[list[str]] = None,
) -> list[Path]:
    if allowed_ext is None:
        allowed_ext = []

        if include_images:
            allowed_ext.extend(IMAGE_EXT)
        if include_videos:
            allowed_ext.extend(VIDEO_EXT)

    if not allowed_ext:
        raise ValueError("No file extension provided")

    path = Path(path)

    files = list(path.rglob("*") if recursive else path.glob("*"))
    files = [file for file in files if file.suffix.lower() in allowed_ext]

    return files
