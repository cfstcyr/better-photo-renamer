from argparse import ArgumentParser

arg_parser = ArgumentParser()

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
    type=bool,
    default=False,
    help="Recursively scan directory",
)

input_args.add_argument(
    "--tz",
    type=str,
    default="Europe/Paris",
    help="Timezone to use for creation time",
)

output_args = arg_parser.add_argument_group(
    "Output",
    "Output options",
)

output_args.add_argument(
    "--filename",
    type=str,
    default="<date>_<filename>",
    help="New filename format",
)
