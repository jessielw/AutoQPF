from pathlib import Path
from pymediainfo import MediaInfo
from typing import Union
import platform

from auto_qpf.long_path import check_for_long_path
from auto_qpf.qpf_exceptions import (
    ImproperChapterError,
    NoChapterDataError,
    ChapterIndexError,
)
from auto_qpf.generate_chapters import ChapterGenerator


class QpfGenerator:
    """
    Generates QPF file, accepted formats are media or OGM text.

    Public method: generate_qpf
    """

    def generate_qpf(
        self,
        file_input: Union[Path, str],
        file_output: Union[Path, str] = None,
        write_to_disk: bool = True,
        fps: Union[int, float] = 23.976,
        auto_detect_fps: bool = True,
        generate_chapters: bool = True,
    ):
        """Creates chapter QPF and returns the path to the output file.

        Args:
            file_input (Union[Path, str]): File input.
            file_output (Union[Path, str], optional): File output. Defaults to None (will auto create name).
            write_to_disk (bool, optional): If this is set, writes to disk, if not it'll return an object with the qpf.
            fps (Union[int, float], optional): Source FPS. Defaults to 23.976. If auto_detect_fps is true and
            input is a not a .txt file, this will be over-ridden automatically.
            auto_detect_fps (bool, optional): Auto detects non text based sources if a video track is present.
            Defaults to True.
            generate_chapters (bool, optional): When enabled this will run a helper class to extract and/or generate new
            new chapters as needed to create a qpf code for.
        """
        # check if we're on a windows platform, if so check for long path support
        if platform.system() == "Windows":
            long_path = check_for_long_path()
            if not long_path:
                print(
                    "WARNING: Long path is not enabled for this OS. This can cause issues for paths greater > 260 characters."
                )

        # convert file_input to Path object
        file_input = Path(file_input)

        # auto generate file output if none was provided
        if not file_output:
            file_output = self._auto_output(file_input)

        # check if input is a text file vs a media file
        if file_input.suffix == ".txt":
            auto_detect_fps = False
            time_codes = self._get_time_codes_text(file_input)
        else:
            media_info = MediaInfo.parse(file_input, parse_speed=0.1)
            detect_fps = self._get_fps(media_info)

            if generate_chapters:
                file_input = ChapterGenerator().generate_ogm_chapters(
                    media_info_obj=media_info,
                    extract_tagged=False,
                    output_path=file_output.with_name(
                        file_output.stem + "_chapters"
                    ).with_suffix(".qpf"),
                )
                time_codes = self._get_time_codes_text(file_input)
            else:
                time_codes = self._get_time_codes_media_file(media_info)

        # if we're auto detecting fps attempt to update fps
        if auto_detect_fps:
            if detect_fps:
                fps = detect_fps

        # if no time codes are detected
        if not time_codes:
            raise NoChapterDataError("Could not detect chapter data from input")

        # get qpf list
        qpf_list = self._process_time_codes(time_codes, fps)

        # if we're writing to disk return the path to the output
        if write_to_disk:
            return self._write_qpf(file_output, qpf_list)

        # if we're not return the list of generated qpf frame positions
        else:
            return qpf_list

    def _process_time_codes(self, time_codes: list, fps: Union[float, str]):
        converted_time_codes = []
        for code in time_codes:
            convert_time = self._calculate_frame_position(code, fps)
            converted_time_codes.append(convert_time)
        return converted_time_codes

    def _get_time_codes_media_file(self, media_info: MediaInfo.parse):
        time_code_list = []
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
    def _get_fps(media_info: MediaInfo.parse):
        fps = None
        video_track_count = media_info.general_tracks[0].count_of_video_streams
        if video_track_count and int(video_track_count) > 0:
            fps = media_info.video_tracks[0].frame_rate
            if fps:
                if "." in fps:
                    fps = float(fps)
                else:
                    fps = int(fps)
        return fps

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
        return output
