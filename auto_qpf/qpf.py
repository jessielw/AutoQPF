from pathlib import Path
from pymediainfo import MediaInfo
from typing import Union

from auto_qpf.qpf_exceptions import (
    ImproperChapterError,
    NoChapterDataError,
    ChapterIndexError,
)


class QpfGenerator:
    def generate_qpf(
        self,
        file_input: Union[Path, str],
        file_output: Union[Path, str] = None,
        fps: Union[int, float] = 23.976,
    ):
        file_input = Path(file_input)
        if not file_output:
            file_output = self._auto_output(file_input)

        if file_input.suffix == ".txt":
            time_codes = self._get_time_codes_text(file_input)
        else:
            time_codes = self._get_time_codes_media_file(file_input)

        if not time_codes:
            raise NoChapterDataError("Could not detect chapter data from input")

        qpf_list = self._process_time_codes(time_codes, fps)
        self._write_qpf(file_output, qpf_list)

    def _process_time_codes(self, time_codes: list, fps: Union[float, str]):
        converted_time_codes = []
        for code in time_codes:
            convert_time = self._calculate_frame_position(code, fps)
            converted_time_codes.append(convert_time)
        return converted_time_codes

    @staticmethod
    def _auto_output(file_input: Path):
        return file_input.parent / Path(file_input.name).with_suffix(".qpf")

    @staticmethod
    def _get_time_codes_text(file_input: Path):
        time_code_list = []
        with open(file_input, "rt", encoding="utf-8") as txt_file:
            time_codes = txt_file.readlines()
            for num, chap in enumerate(time_codes):
                if num % 2 == 0:
                    time_code = chap.split("=")
                    if len(time_code) == 2:
                        time_code = time_code[1].replace("\n", "")
                        time_code_list.append(time_code)
                    else:
                        raise ImproperChapterError(
                            "Input file is an improper or corrupt chapter file."
                        )
        return time_code_list

    @staticmethod
    def _get_time_codes_media_file(file_input: Path):
        time_code_list = []
        media_info = MediaInfo.parse(file_input, parse_speed=0.1)
        menu_stream_count = media_info.general_tracks[0].count_of_menu_streams
        if menu_stream_count and int(menu_stream_count) > 0:
            chapter_data = media_info.menu_tracks[0].to_data()
            if chapter_data:
                chapter_data = list(chapter_data.keys())
                try:
                    get_index = chapter_data.index("chapters_pos_end") + 1
                    split_list = chapter_data[get_index:]
                    for time_code in split_list:
                        time_code_list.append(time_code.replace("_", ":"))
                except ValueError:
                    raise ChapterIndexError(
                        "Cannot find the position of chapters_pos_end"
                    )
            else:
                raise NoChapterDataError("Input file has no chapter data")
        else:
            raise NoChapterDataError("Input file has no chapter data")
        return time_code_list

    @staticmethod
    def _calculate_frame_position(time_code: str, fps):
        # Formula: FramePosition = time-code (seconds) * fps
        # Split the time-code into hours, minutes, seconds, and milliseconds
        hours, minutes, seconds = map(float, time_code.split(":"))
        seconds += (hours * 3600) + (minutes * 60)

        # Calculate the frame position
        # We round to handle the floating point values as this is how it's done in MeGUI
        frame_position = round(seconds * fps)
        return frame_position

    @staticmethod
    def _write_qpf(output: Path, qpf_list: list):
        with open(output, "wt", encoding="utf-8") as qpf_file:
            for qpf_code in qpf_list:
                qpf_file.write(f"{qpf_code} K\n")
