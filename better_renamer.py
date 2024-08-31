import pandas as pd
from pillow_heif import register_heif_opener
from tqdm import tqdm
from src.tag_extractor import TagExtractor, Tags
from src.cache import PandasPickleCache

register_heif_opener()

PATH = "/Users/charles-francoisst-cyr/Library/CloudStorage/ProtonDrive-cfstcyr@pm.me-folder/Photos/2024/07 Juillet - Chamonix"

NEW_FILENAME_REGEX = r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})_(.*)_(\d{3})\.(.*)"

file_cache = PandasPickleCache("cache.pkl")


# def load_images(path: str) -> pd.DataFrame:
#     files = os.listdir(path)

#     df = pd.DataFrame(files, columns=["filename"])
#     df = df[df["filename"] != ".DS_Store"]

#     df["path"] = df["filename"].map(lambda filename: os.path.join(path, filename))

#     return df


def extract_images_info(df: pd.DataFrame) -> pd.DataFrame:
    df["ext"] = df["path"].str.split(".").str[-1]
    tqdm.pandas(desc="Extracting tags")
    df["tags"] = df["path"].map(
        lambda path: TagExtractor.create(path, file_cache).extract(path)
    )

    for tag in Tags.__annotations__.keys():
        df[tag] = df["tags"].map(lambda tags: tags[tag] if tag in tags else None)

    df = df.drop(columns=["tags"])
    df["creation_time"] = pd.to_datetime(df["creation_time"], utc=True)

    df["already_renamed"] = df["filename"].str.match(NEW_FILENAME_REGEX)

    df = df.sort_values(by=["creation_time", "id"]).reset_index(drop=True)

    return df


def create_new_filenames(df: pd.DataFrame, name: str) -> pd.DataFrame:
    index = pd.Index(range(len(df)))
    df["new_filename"] = (
        df["creation_time"].dt.strftime("%Y-%m-%d_%H-%M-%S")
        + "_"
        + name.replace(" ", "-")
        + "_"
        + index.astype("str").str.pad(3, "left", "0")
    )
    df["new_filename"] += "." + df["ext"]

    return df


def _match_live_photos_exact(
    live_photos: pd.DataFrame, non_live_photos: pd.DataFrame
) -> pd.DataFrame:
    match = pd.Index.intersection(live_photos.index, non_live_photos.index)

    matched_live_photos = live_photos.loc[match]
    matched_non_live_photos = non_live_photos.loc[match]
    matched_non_live_photos = matched_non_live_photos[
        ~matched_non_live_photos.index.duplicated(keep="first")
    ]

    matched_live_photos["match_index"] = matched_non_live_photos.loc[match, "index"]

    return matched_live_photos


def split_live_photos(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = df.reset_index()
    df.index = df["creation_time"]

    live_photos = df[df["is_live_photo"]]
    non_live_photos = df[~df["is_live_photo"]]

    initial_live_photos_count = len(live_photos)

    matched_live_photos_exact = _match_live_photos_exact(live_photos, non_live_photos)

    live_photos = live_photos[~live_photos.index.isin(matched_live_photos_exact.index)]
    unique_non_live_photos = non_live_photos[
        ~non_live_photos.index.duplicated(keep="first")
    ]

    match = unique_non_live_photos.index.get_indexer(
        live_photos.index, method="nearest"
    )
    live_photos["match_index"] = unique_non_live_photos.iloc[match]["index"].values

    live_photos = pd.concat([live_photos, matched_live_photos_exact])

    live_photos.index = live_photos["index"]
    live_photos = live_photos.drop(columns=["index"])
    non_live_photos.index = non_live_photos["index"]
    non_live_photos = non_live_photos.drop(columns=["index"])

    if len(live_photos) != initial_live_photos_count:
        print(
            f"Warning: {initial_live_photos_count - len(live_photos)} live photos could not be matched"
        )

    return non_live_photos, live_photos


# df = load_images(PATH)
# df = extract_images_info(df)

# df = df.reset_index(drop=True)

# initial_size = len(df)

# photos, live_photos = split_live_photos(df)

# photos = create_new_filenames(photos, "Turin")
# photos_match = photos.copy()
# photos_match = photos_match.loc[live_photos["match_index"]]
# photos_match.index = live_photos.index

# live_photos["new_filename"] = (
#     photos_match["new_filename"].str.rsplit(".", n=1).str[0]
#     + "_live."
#     + live_photos["ext"]
# )

# all_photos = pd.concat([photos, live_photos]).sort_index()
# total_size = len(all_photos)

# if initial_size != total_size:
#     raise ValueError(f"Initial size: {initial_size}, total size: {total_size}")

# all_photos = all_photos[all_photos["filename"] != all_photos["new_filename"]]

# if total_size != len(all_photos):
#     print(f"{total_size - len(all_photos)} files already have the correct name")

# if len(all_photos) == 0:
#     print("All files are already correctly named")
#     exit()

# if pd.concat([all_photos["filename"], all_photos["new_filename"]]).duplicated().any():
#     print(all_photos[["filename", "new_filename"]].head(10))
#     raise ValueError("Duplicate filenames")

# print(f"Preview rename of first 10 images out of {len(all_photos)}:")
# print(all_photos[["filename", "new_filename"]].head(10))

# if input("Proceed? [y/n] (default: n) ") != "y":
#     print("Aborted")
#     exit()

# for i, row in all_photos.iterrows():
#     os.rename(
#         os.path.join(PATH, row["filename"]), os.path.join(PATH, row["new_filename"])
#     )

# print("Done")
