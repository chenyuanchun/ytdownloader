import argparse
import logging
import pathlib
import shelve

from collections.abc import Iterable
from pytube import YouTube, Channel, Playlist


def download_video(video_url: str, audio_only=True, output_path=pathlib.Path.cwd()):
    video_stream = None
    try:
        yt = YouTube(video_url)

        if audio_only:
            video_stream = yt.streams.filter(only_audio=True).first()
        else:
            video_stream = yt.streams.get_highest_resolution()

        # Get the default filename
        # video_filename = video_stream.default_filename

        f = video_stream.download(str(output_path))
        logger.info(f"Video downloaded successfully to: {f}")

        if audio_only:
            downloaded_filename = pathlib.Path(f)
            mp3_filename = downloaded_filename.with_suffix('.mp3')
            logger.info(f'Renaming file {downloaded_filename} to {mp3_filename}...')
            downloaded_filename.rename(mp3_filename)
        return True
    except Exception as e:
        logger.error(f"Failed to download {video_stream.default_filename if video_stream else video_url}, Error: {e}", exc_info=True)
        return False


def download_multiple(url_list: Iterable[str], directory: pathlib.Path, audio_only=True):
    if not directory.exists():
        directory.mkdir(exist_ok=True)

    # init downloading status
    status_db = directory / '.status'
    with shelve.open(str(status_db)) as download_status:
        for url in url_list:
            status = download_status.get(url)
            if status:
                logger.info(f'video {url} has downloaded, skipped ...')
                continue
            elif status is None:
                download_status[url] = False

            ok = download_video(url, audio_only=audio_only, output_path=directory)
            download_status[url] = ok


def download_playlist(list_url: str, audio_only=True, output_path=pathlib.Path.cwd(), ord_num=False):
    plist = Playlist(list_url)

    title = plist.title
    if not title:
        logger.info('Cannot get the title, playlist url may be invalid')
        return

    playlist_dir = output_path / title
    logger.info(f'Downloading play list: {title} to {playlist_dir}...')
    download_multiple(plist.video_urls, playlist_dir, audio_only)


def download_channel(channel_url: str, output_path: pathlib.Path, audio_only=True):
    channel = Channel(channel_url)
    if not channel.title:
        logger.info('Cannot get the title, channel url may be invalid')
        return

    channel_dir = output_path / channel.title
    logger.info(f'Download channel: {channel.title} to {channel_dir} ...')
    download_multiple(channel.video_urls, channel_dir, audio_only)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='youtube url')
    parser.add_argument('-a', '--audio', action='store_true', help='download audio only')
    parser.add_argument('-l', '--list', action='store_true', help='download play list')
    parser.add_argument('-c', '--channel', action='store_true', help='download channel')
    parser.add_argument('-o', '--output', action='store', help='the download directory')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] - %(message)s',  # Set the log format
        datefmt='%Y-%m-%d %H:%M:%S'  # Set the date/time format
    )
    logger = logging.getLogger()

    args = parser.parse_args()
    download_dir = pathlib.Path(args.output) if args.output else pathlib.Path.cwd()
    if args.list:
        download_playlist(args.url, args.audio, download_dir)
    elif args.channel:
        download_channel(args.url, download_dir, args.audio)
    else:
        download_video(args.url, args.audio, download_dir)
    # download_playlist(args.url, args.audio, pathlib.Path(args.output))
