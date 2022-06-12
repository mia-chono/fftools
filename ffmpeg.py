from process import Process


class FFmpeg:
    def __init__(self, bin_path: str = "ffmpeg", **options):
        self.err = None
        self.pipe = None
        self.bin_path = bin_path
        self.options = options
        self.commands = ["-y"]

    def add_command(self, command: str) -> "FFmpeg":
        for c in command.split(" "):
            self.commands.append(c)
        return self

    def add_commands(self, commands: list) -> "FFmpeg":
        for command in commands:
            self.add_command(command)
        return self

    def add_file(self, file: str) -> "FFmpeg":
        return self.add_commands(["-i", "'{}'".format(file)])

    def add_files(self, files: list) -> "FFmpeg":
        for file in files:
            self.add_file(file)
        return self

    def add_stream(self, stream: str) -> "FFmpeg":
        return self.add_file(stream)

    def set_audio_quality(self, quality: str) -> "FFmpeg":
        return self.add_commands(["-q:a", quality])

    def set_video_quality(self, quality: str) -> "FFmpeg":
        return self.add_commands(["-q:v", quality])

    def map_audio_metadata(self, select_track: int = 0, options={}) -> "FFmpeg":
        map_content = [
            "-map",
            "a",
            "-map_metadata",
            "{}".format(select_track),
            "-map_metadata:s:a",
            "{}:s:a".format(select_track),
        ]
        for key, value in options.items():
            map_content += [
                "-metadata:s:a:{track}".format(track=select_track),
                "{key}='{value}'".format(key=key, value=value)
            ]
        return self.add_commands(map_content)

    def map_video_metadata(self, select_track: int = 0, options={}) -> "FFmpeg":
        map_content = [
            "-map",
            "v",
            "-map_metadata",
            "{}".format(select_track),
            "-map_metadata:s:v",
            "{}:s:v".format(select_track),
        ]
        for key, value in options.items():
            map_content += [
                "-metadata:s:v:{track}".format(track=select_track),
                "{key}='{value}'".format(key=key, value=value)
            ]
        return self.add_commands(map_content)

    def output_audio_file(self, codec: str = "copy", file: str = "audio.aac") -> "FFmpeg":
        return self.add_commands(["-acodec", "copy", "'{}'".format(file)])

    def output_video_file(self, codec: str = "copy", file: str = "video.mp4") -> "FFmpeg":
        return self.add_commands(["-c", "copy", "'{}'".format(file)])

    def command_builder(self, with_bin_path: bool = False) -> str:
        return "{} {}".format(self.bin_path, " ".join(self.commands)) if with_bin_path else " ".join(self.commands)

    def run(self, monitor: callable = None, **options):
        with Process(self.bin_path, self.command_builder(), monitor, **options) as process:
            self.pipe, self.err = process.run()
