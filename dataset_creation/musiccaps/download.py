import datetime as dt
import os
from concurrent.futures import as_completed, ThreadPoolExecutor

import pandas as pd
from tqdm import tqdm
from yt_dlp import YoutubeDL


def _download_audio(ytid, start, end, out_dir):
    start_dt, end_dt = dt.timedelta(seconds=start), dt.timedelta(seconds=end)
    ydl_opts = {
        "outtmpl": f"{out_dir}/{ytid}_{start}.%(ext)s",
        "format": "bestaudio[ext=webm]/bestaudio/best",
        "external_downloader": "ffmpeg",
        "external_downloader_args": [
            "-ss",
            str(start_dt),
            "-to",
            str(end_dt),
            "-loglevel",
            "panic",
        ],
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }
        ],
        "quiet": True,
        "no-mtime": True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={ytid}"])
    except KeyboardInterrupt:
        raise
    except Exception:
        with open(f"{out_dir}/../error.log", "a") as f:
            f.write(f"{ytid}\n")
        pass


def download_concurrent(ytids, st_list, ed_list, save_path, desc=None):
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(_download_audio, ytid, start, end, save_path)
            for ytid, start, end in zip(ytids, st_list, ed_list)
        ]
        for _ in tqdm(as_completed(futures), total=len(ytids), desc=desc):
            pass


def dl_audioset(metadata_df, save_path):
    os.makedirs(save_path, exist_ok=True)
    targets = []
    for idx in range(len(metadata_df)):
        instance = metadata_df.iloc[idx]
        outtmpl = (
            f"{save_path}/{instance.ytid}_{int(instance.start_s)}.wav"
        )
        if not os.path.exists(outtmpl):
            targets.append(instance)

    print(
        f"{len(metadata_df) - len(targets)} audio files found. "
        f"Downloading {len(targets)} missing audio files"
    )

    metadata_df = pd.DataFrame(targets)
    yids = metadata_df["ytid"]

    start_time = metadata_df.start_s.astype(int)
    end_time = metadata_df.end_s.astype(int)
    download_concurrent(yids, start_time, end_time, save_path)
