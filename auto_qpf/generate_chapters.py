import re
from pathlib import Path
from datetime import timedelta

from pymediainfo import MediaInfo

from auto_qpf.enums import ChapterType


class ChapterGenerator:
    def generate_ogm_chapters(
        self,
        media_info_obj: MediaInfo,
        output_path: Path,
        chapter_chunks: float = 5.0,
        extract_tagged: bool = True,
        extract_named: bool = True,
        extract_numbered: bool = True,
    ):
        """
        Detect rather or not input file has numbered, named, tagged chapters or no chapters.

        If needed this will generate OGM/txt based chapters in the format:
        Chapter 01
        Chapter 02
        etc...

        Args:
            media_info_obj (MediaInfo): MediaInfo.parse() object.
            output_path (Path): Output path for the *.txt chapter file.
            chapter_chunks (float): Chunks to create chapters automatically in percentage.
            Defaults to 5.0.
            If a movie is an hour and a half long this would give you chapters about every 11 minutes.
            extract_tagged (bool, optional): If tagged chapters are accepted and the input has them extract those.
            Defaults to True.
            extract_named (bool, optional): If named chapters are accepted and the input has them extract those.
            Defaults to True.
            extract_numbered (bool, optional): If numbered chapters are accepted (in the correct format) and the input has them extract those.
            Defaults to True.
        """

        get_chapters = self._get_media_info_obj_chapters(media_info_obj)

        # if chapters was detected determine the type and if we want to keep them
        if get_chapters:
            chapter_type = self._determine_chapter_type(get_chapters)
            if chapter_type[0] == ChapterType.NAMED:
                if extract_named:
                    return self._extract_chapters(
                        chapter_type[0], chapter_type[1], output_path
                    )
                elif not extract_named:
                    generate_chapters = self._generate_chapters(
                        media_info_obj, chapter_chunks
                    )
                    return self._write_new_numbered_chapters(
                        generate_chapters, output_path
                    )

            if chapter_type[0] == ChapterType.NUMBERED:
                if extract_numbered:
                    try:
                        return self._extract_chapters(
                            chapter_type[0], chapter_type[1], output_path
                        )
                    except IndexError:
                        generate_chapters = self._generate_chapters(
                            media_info_obj, chapter_chunks
                        )
                        return self._write_new_numbered_chapters(
                            generate_chapters, output_path
                        )
                elif not extract_numbered:
                    generate_chapters = self._generate_chapters(
                        media_info_obj, chapter_chunks
                    )
                    return self._write_new_numbered_chapters(
                        generate_chapters, output_path
                    )

            if chapter_type[0] == ChapterType.TAGGED:
                if extract_tagged:
                    return self._extract_chapters(
                        chapter_type[0], chapter_type[1], output_path
                    )
                elif not extract_tagged:
                    generate_chapters = self._generate_chapters(
                        media_info_obj, chapter_chunks
                    )
                    return self._write_new_numbered_chapters(
                        generate_chapters, output_path
                    )

        # if no chapters was detected
        elif not get_chapters:
            generate_chapters = self._generate_chapters(media_info_obj, chapter_chunks)
            return self._write_new_numbered_chapters(generate_chapters, output_path)

    def _determine_chapter_type(self, media_info_menu: dict):
        menu = self._get_menu_info_only(media_info_menu)
        menu_str = " ".join(menu[2])
        menu_str_reversed = " ".join(reversed(menu[2]))

        if re.search(r"\d+:\d+:\d+\.\d+", menu_str):
            return ChapterType.TAGGED, menu[0]

        else:
            try:
                # check for numbered chapters
                chapters_start_numbered = re.search(
                    r"chapter\s*(\d+)", menu_str, re.IGNORECASE
                ).group(1)

                chapters_end_numbered = re.search(
                    r"chapter\s*(\d+)",
                    menu_str_reversed,
                    re.IGNORECASE,
                ).group(1)

                return (
                    ChapterType.NUMBERED,
                    menu[0],
                    chapters_start_numbered,
                    chapters_end_numbered,
                )

            # if chapters are not numbered assume Named (since we check for tagged chapters already)
            except AttributeError:
                return ChapterType.NAMED, menu[0]

    def _generate_chapters(self, media_info: MediaInfo, chapter_chunks: float):
        duration_ms = int(media_info.general_tracks[0].duration) / 1000

        # Calculate the duration for each chapter
        chunk_percentage = chapter_chunks / 100
        chapter_interval = duration_ms * chunk_percentage

        chapter_dict = {1: "00:00:00.000"}

        # Calculate the number of chapters based on the chunk percentage
        num_chapters = int(1 / chunk_percentage)

        for i in range(2, num_chapters + 1):
            chapter_seconds = i * chapter_interval
            formatted_time = self._convert_to_time_format(chapter_seconds)
            # Round the seconds part to 3 decimal places
            formatted_time = ":".join(
                part.zfill(2) for part in formatted_time.split(":")
            )
            chapter_dict[i] = formatted_time

        return chapter_dict

    @staticmethod
    def _get_media_info_obj_chapters(media_info_obj: MediaInfo):
        menu_stream_count = media_info_obj.general_tracks[0].count_of_menu_streams
        if menu_stream_count and int(menu_stream_count) > 0:
            return media_info_obj.menu_tracks[0].to_data()
        return None

    @staticmethod
    def _get_menu_info_only(media_info_menu: dict):
        chapter_dict = {}
        chapters_only = list(media_info_menu.keys()).index("chapters_pos_end") + 1
        chapter_keys = list(media_info_menu.keys())[chapters_only:]
        chapter_values = list(media_info_menu.values())[chapters_only:]

        for val, key in zip(chapter_keys, chapter_values, strict=True):
            chapter_dict.update({val: key})

        return chapter_dict, chapter_keys, chapter_values

    @staticmethod
    def _write_new_numbered_chapters(chapter_dict: dict, output_path: Path):
        output_path = Path(output_path)

        with open(output_path, "wt+", encoding="utf-8") as chapt_out:
            for num, tag in enumerate(chapter_dict.keys(), start=1):
                num = str(num).zfill(2)
                tag = chapter_dict[tag]

                chapt_out.write(f"CHAPTER{num}={tag}\nCHAPTER{num}NAME=Chapter {num}\n")

        if output_path.is_file():
            return output_path

    @staticmethod
    def _extract_chapters(
        chapter_type: ChapterType, chapter_dict: dict, output_path: Path
    ):
        output_path = Path(output_path)

        # if we have numbered chapters we're going to check that they are in the correct
        # format of Chapters 01, Chapters 02, etc...
        if chapter_type == ChapterType.NUMBERED:
            first_chapter_num = list(chapter_dict.values())[0].split(" ")[1].strip()
            if first_chapter_num != "01":
                new_chapter_dict = {}
                for num, chap in enumerate(chapter_dict, start=1):
                    new_chapter_dict.update({chap: f"Chapter {str(num).zfill(2)}"})
                chapter_dict = new_chapter_dict

        # extract chapters
        with open(output_path, "wt+", encoding="utf-8") as chapt_out:
            for num, tag in enumerate(chapter_dict, start=1):
                num = str(num).zfill(2)
                l_tag = tag.replace("_", ":")[:-3]
                r_tag = tag[-3:]
                new_tag = f"{l_tag}.{r_tag}"
                value = str(chapter_dict[tag])
                if ":" in value:
                    language_pattern = re.compile(r"^([a-zA-Z]{2,3}:(\s*)?){1,2}")
                    value = re.sub(language_pattern, "", value).strip()
                chapt_out.write(f"CHAPTER{num}={new_tag}\nCHAPTER{num}NAME={value}\n")

        if output_path.is_file():
            return output_path

    @staticmethod
    def _convert_to_time_format(seconds):
        td = timedelta(seconds=seconds)
        # Format the timedelta with three decimal places for seconds
        formatted_time = str(td).rsplit(".", 1)[0] + f".{td.microseconds // 1000:03}"
        return formatted_time
