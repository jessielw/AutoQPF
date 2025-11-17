# AutoQPF

A Python library for generating QPF (QP file) frame time codes for use with x264/x265 encoders, with automatic chapter detection and generation.

## Installation

```bash
pip install AutoQPF
```

## Uninstall

```bash
pip uninstall AutoQPF
```

---

## Quick Start

### Basic Usage

```python
from auto_qpf.qpf import QpfGenerator

# Generate QPF from a media file (supports virtually any media file)
qpf = QpfGenerator().generate_qpf(file_input="path/to/file.mkv")

# Generate QPF from a chapter file (OGM format)
qpf = QpfGenerator().generate_qpf(file_input="path/to/chapters.txt")
```

### Error Handling

```python
from auto_qpf.qpf import (
    QpfGenerator,
    ChapterIndexError,
    ImproperChapterError,
    NoChapterDataError
)

try:
    qpf = QpfGenerator().generate_qpf(file_input="path/to/file.mkv")
except ChapterIndexError:
    print("Issue getting the correct index from the chapters")
except ImproperChapterError:
    print("Input has improper or corrupted chapters")
except NoChapterDataError:
    print("Input has no chapter data")
```

---

## API Reference

### `QpfGenerator.generate_qpf()`

Generate QPF frame time codes from media files or chapter files.

#### Parameters

| Parameter           | Type    | Default      | Description                                                                                                                |
| ------------------- | ------- | ------------ | -------------------------------------------------------------------------------------------------------------------------- |
| `file_input`        | `str`   | **Required** | Path to the input file (media or OGM chapter file)                                                                         |
| `file_output`       | `str`   | `None`       | Output path for the QPF file. If not specified, automatically generated based on input                                     |
| `write_to_disk`     | `bool`  | `True`       | If `False`, returns a list of converted chapter time codes instead of writing to disk (ignores `file_output`)              |
| `fps`               | `float` | `23.976`     | Frame rate to use. Required when using `.txt` (OGM) format. Auto-detected for media files with video tracks                |
| `auto_detect_fps`   | `bool`  | `True`       | Override user-provided FPS with auto-detected value from media file                                                        |
| `generate_chapters` | `bool`  | `True`       | Automatically generate OGM chapter file alongside QPF, correcting improper chapter numbering and extracting named chapters |

---

### `ChapterGenerator.generate_ogm_chapters()`

Generate or extract OGM-formatted chapter files from media.

> **Note:** Currently requires a `MediaInfo.parse()` object. Future versions may support direct file input.

#### Parameters

| Parameter          | Type        | Default      | Description                                                                                        |
| ------------------ | ----------- | ------------ | -------------------------------------------------------------------------------------------------- |
| `media_info_obj`   | `MediaInfo` | **Required** | Parsed `pymediainfo` MediaInfo object                                                              |
| `output_path`      | `Path`      | **Required** | Output path for the OGM chapters file (must have `.txt` suffix)                                    |
| `chapter_chunks`   | `float`     | `5.0`        | Percentage of file duration per auto-generated chapter (e.g., `5.0` = chapter every 5% of runtime) |
| `extract_tagged`   | `bool`      | `True`       | Extract detected tagged chapters from source                                                       |
| `extract_named`    | `bool`      | `True`       | Extract detected named chapters from source                                                        |
| `extract_numbered` | `bool`      | `True`       | Extract detected numbered chapters from source (validates correct format)                          |
| `write_to_file`    | `bool`      | `True`       | If `False`, returns chapter content as string instead of writing to disk                           |

**Behavior:** If any `extract_*` parameter is set to `False` and that chapter type is detected, the program will automatically generate clean numbered chapters instead.

#### Example

```python
from auto_qpf.generate_chapters import ChapterGenerator
from pymediainfo import MediaInfo

media_info = MediaInfo.parse("path/to/file.mkv")

# Write chapter file to disk
chapter_path = ChapterGenerator().generate_ogm_chapters(
    media_info_obj=media_info,
    output_path="chapters.txt"
)
print(f"Chapters written to: {chapter_path}")

# Get chapter content as string without writing
chapter_content = ChapterGenerator().generate_ogm_chapters(
    media_info_obj=media_info,
    output_path="",  # Not used when write_to_file=False
    write_to_file=False
)
print(chapter_content)
```

---

## License

See [LICENSE](LICENSE) file for details.
