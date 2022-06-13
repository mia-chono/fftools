from process import Process


class FFmpeg:
    """
    FFmpeg wrapper, used to simplify the using of ffmpeg.
    """
    def __init__(self, bin_path: str = 'ffmpeg', **options):
        self.err = None
        self.pipe = None
        self.bin_path = bin_path
        self.options = options
        self.commands = ['-y']

    def add_command(self, command: str) -> 'FFmpeg':
        """
        Add a command to the command list.
        1. you can add param by param like:
        ```
            add_command('-i')

            add_command('"file.mp4"')
        ```
        2.you can give a full command like:
        ```
            add_command('-i "file.mp4"')
        ```

        :param command: the command to execute with the ffmpeg
        :return: FFmpeg
        """
        for c in str(command).split(' '):
            self.commands.append(c)
        return self

    def add_commands(self, commands: list[str]) -> 'FFmpeg':
        """
        Add a list of commands to the command list.
        :param commands: list of strings to add to the command list
        :return: FFmpeg
        """
        for command in commands:
            self.add_command(command)
        return self

    def add_file(self, file: str) -> 'FFmpeg':
        """
        Add -i command
        :param file: file path
        :return: FFmpeg
        """
        return self.add_commands(['-i', '"{}"'.format(file)])

    def add_files(self, files: list) -> 'FFmpeg':
        """
        Add a list of files to the command list.
        :param files: list of paths
        :return: FFmpeg
        """
        for file in files:
            self.add_file(file)
        return self

    def add_stream(self, stream: str) -> 'FFmpeg':
        """
        Add a stream to the command list.
        :param stream: link to the stream
        :return: FFmpeg
        """
        return self.add_file(stream)

    def set_audio_quality(self, quality: int = 0) -> 'FFmpeg':
        """
        Set the audio quality to download.
        :param quality: by default it's 0, the best quality.
        :return: FFmpeg
        """
        return self.add_commands(['-q:a', quality])

    def set_video_quality(self, quality: int = 0) -> 'FFmpeg':
        """
        Set the video quality to download.
        :param quality: by default it's 0, the best quality.
        :return: FFmpeg
        """
        return self.add_commands(['-q:v', quality])

    def map_audio_metadata(self, select_track: int = 0, options={}) -> 'FFmpeg':
        """
        When used with 1080p video, you can map the audio metadata to the extracted audio.
        :param select_track: use by default 0, the global metadata.
        :param options: dict of metadata to map with the audio. (example: language="en")
        :return: FFmpeg
        """
        map_content = [
            '-map',
            'a',
            '-map_metadata',
            "{}".format(select_track),
            '-map_metadata:s:a',
            '{}:s:a'.format(select_track),
        ]
        for key, value in options.items():
            map_content += [
                '-metadata:s:a:{track}'.format(track=select_track),
                '{key}="{value}"'.format(key=key, value=value)
            ]
        return self.add_commands(map_content)

    def map_video_metadata(self, select_track: int = 0, options={}) -> 'FFmpeg':
        """
        When used with 1080p video, you can map the video metadata to the extracted audio.
        :param select_track: use by default 0, the global metadata.
        :param options: dict of metadata to map with the video. (example: title="My title")
        :return: FFmpeg
        """
        map_content = [
            '-map',
            'v',
            '-map_metadata',
            "{}".format(select_track),
            '-map_metadata:s:v',
            '{}:s:v'.format(select_track),
        ]
        for key, value in options.items():
            map_content += [
                '-metadata:s:v:{track}'.format(track=select_track),
                '{key}="{value}"'.format(key=key, value=value)
            ]
        return self.add_commands(map_content)

    def output_audio_file(self, codec: str = 'copy', file: str = 'audio.aac') -> 'FFmpeg':
        """
        Set the output audio file with copy codec.
        :param codec: codec to use for the output file.
        :param file: output file path
        :return: FFmpeg
        """
        return self.add_commands(['-acodec', '{}'.format(codec), '"{}"'.format(file)])

    def output_video_file(self, codec: str = 'copy', file: str = 'video.mp4') -> 'FFmpeg':
        """
        Set the output video file with copy codec.
        :param codec: codec to use for the output file.
        :param file: output file path
        :return: FFmpeg
        """
        return self.add_commands(['-c', '{}'.format(codec), '"{}"'.format(file)])

    def command_builder(self, with_bin_path: bool = False) -> str:
        """
        Create a concatenated command string to execute.
        Possibility to add the bin path.
        :param with_bin_path: should the bin path be added to the command string?
        :return: concatenated command string
        """
        return '{} {}'.format(self.bin_path, ' '.join(self.commands)) if with_bin_path else ' '.join(self.commands)

    def run(self, monitor: callable = None, **options) -> None:
        """
        Create a subprocess and run the command.
        :param monitor: callback function to monitor the process.
        :param options: options to pass to the subprocess.
        """
        with Process(self.bin_path, self.command_builder(), monitor, **options) as process:
            self.pipe, self.err = process.run()
