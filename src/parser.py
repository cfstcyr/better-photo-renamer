from argparse import ArgumentParser

from src.file_operator.file_operator import FILE_OPERATORS

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
    action="store_true",
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

arg_parser.add_argument(
    "--operator",
    "-o",
    choices=FILE_OPERATORS.keys(),
    default="rename",
    help="Operation to perform. Use 'dry-run' to simulate renaming",
)

arg_parser.add_argument(
    "--ask-confirm",
    action="store_true",
    help="Ask for confirmation before renaming files",
)
