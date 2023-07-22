# AutoQPF

Generates QPF frame time codes to be used with x264/x265

## Install

`pip install AutoQPF`

## Uninstall

`pip uninstall AutoQPF`

## Example of how to use AutoQPF

```python
from auto_qpf.qpf import QpfGenerator, ChapterIndexError, ImproperChapterError, NoChapterDataError

# basic ##########################
# media file (virtually any media file)
qpf = QpfGenerator().generate_qpf(file_input="PATH TO FILE.mkv")

# chapter file (ogm format)
qpf = QpfGenerator().generate_qpf(file_input="PATH TO FILE.txt")


# error handling ##################
try:
    qpf = QpfGenerator().generate_qpf(file_input="PATH TO FILE.mkv")

except ChapterIndexError:
    print("Issue getting the correct index from the chapters")

except ImproperChapterError:
    print("Input has improper or corrupted chapters")

except NoChapterDataError:
    print("Input has no chapter data")
```

## AutoQPF .generate_qpf() parameters

`file_input` Required, path of the input file

`file_output` Optional, can specify an output path, if one isn't will automatically create one based on the input

`write_to_disk` Optional, True/False (default is True), if this is set to false the 'file_output' parameter will be ignored and a list of the converter chapter time codes will be returned

`fps` Optional, this should be defined when using '.txt' (ogm) format. If it's a media file + has a video track we will automatically detect the FPS. Default is '23.976'

`auto_detect_fps` Optional, True/False (default is True), this will over ride any user input if the file input is a media file
