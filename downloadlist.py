import argparse
import pathlib

from pytube import YouTube, Playlist


def download_playlist(url, audio_only=True, download_dir=pathlib.Path.cwd()):
    p = Playlist(url)

    if not p.title:
        print('Cannot get the title, playlist url may be invalid')
        return

    playlist_dir = download_dir / p.title
    if not playlist_dir.exists():
        playlist_dir.mkdir(exist_ok=True)

    print(f'Downloading play list: {p.title} to {playlist_dir}...')
    for idx, v in enumerate(p.videos):
        ord_num = str(idx+1).zfill(2)
        try:
            f = v.streams.filter(only_audio=audio_only).first().download(output_path=str(playlist_dir))
            downloaded_filename = pathlib.Path(f)
            mp3_filename = downloaded_filename.with_suffix('.mp3')
            mp3_ord_name = mp3_filename.with_stem(ord_num + mp3_filename.stem)
            print(f'Renaming file {downloaded_filename} to {mp3_ord_name}...')
            downloaded_filename.rename(mp3_ord_name)
        except Exception as e:
            print(f'Error downloading file {v.title}, skipping ...')
            continue


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='youtube url')
    parser.add_argument('-a', '--audio', action='store_true', help='download audio only')
    parser.add_argument('-o', '--output', action='store', help='the download directory')

    args = parser.parse_args()
    download_playlist(args.url, args.audio, pathlib.Path(args.output))

# yt = YouTube(r'https://www.youtube.com/watch?v=rIEwRcfZGSA&list=PLk-ux5lkyDsA7zSluQn9Yax36qpJ7LLSo&index=3')
# video = yt.streams.filter(only_audio=True).first()
# out_file = video.download(output_path='./Download')
