from argparse import ArgumentParser

arg_parser = ArgumentParser()

arg_parser.add_argument(
    "--dir",
    "-d",
    type=str,
    required=True,
    help="Directory to scan for photos",
)

arg_parser.add_argument(
    "--tz",
    type=str,
    default="Europe/Paris",
    help="Timezone to use for creation time",
)

arg_parser.add_argument(
    "--filename",
    type=str,
    default="<date>_<filename>",
    help="New filename format",
)
