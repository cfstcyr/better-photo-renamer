import piexif

codec = "ISO-8859-1"  # or latin-1
IGNORED_TAGS = [
    "thumbnail",
]


def exif_to_tag(exif_dict):
    exif_tag_dict = {}

    for ifd in exif_dict:
        if ifd in IGNORED_TAGS:
            continue
        if exif_dict[ifd] is None:
            continue

        exif_tag_dict[ifd] = {}

        for tag in exif_dict[ifd]:
            try:
                element = exif_dict[ifd][tag].decode(codec)

            except AttributeError:
                element = exif_dict[ifd][tag]

            exif_tag_dict[ifd][piexif.TAGS[ifd][tag]["name"]] = element

    return exif_tag_dict
