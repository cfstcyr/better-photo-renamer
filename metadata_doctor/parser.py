from argparse import ArgumentParser

arg_parser = ArgumentParser()

arg_parser.add_argument(
    "--verbose",
    action="store_true",
    help="Show debug messages",
)

input_args = arg_parser.add_argument_group(
    "Input",
    "Input options",
)

input_args.add_argument(
    "--dir",
    "-d",
    type=str,
    required=True,
    help="Directory to scan for photos",
)

input_args.add_argument(
    "--recursive",
    "-r",
    action="store_true",
    help="Recursively scan directory",
)

input_args.add_argument(
    "--tz",
    type=str,
    default="Europe/Paris",
    help="Timezone to use for creation time",
)

input_args.add_argument(
    "--cache",
    action="store_true",
    help="Use cache for metadata extraction",
)

input_args.add_argument(
    "--include-live-photos",
    action="store_true",
    help="Include live photos",
)
