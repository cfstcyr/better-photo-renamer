# Better Photo Renamer

I started building a small script to organize my photos. Few hours later: data clustering, formal grammar, etc.

## Usage

```bash
python -m better_photo_renamer --help
```

### Example

```bash
python -m better_photo_renamer \
    --dir /my/photos/my-trip \
    --filename "<group>/My trip <index:pad=2> <date:format=\"%Y-%m-%d\">" \
    --group k_means:lat,long \
    -o dry-run
```

In this example, the script will:

1. Read all photos from `/my/photos/my-trip`
2. Cluster them using K-Means with the latitude and longitude of each photo
3. Rename each photo to `My trip <index> <date>`, where:
    - `<group>` is the name of the cluster
    - `<index>` is the index of the photo in the collection (zero-based)
    - `<date>` is the date of the photo in the format `YYYY-MM-DD`
4. Print the new names of the photos without actually renaming them (dry-run)