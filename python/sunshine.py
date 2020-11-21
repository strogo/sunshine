from argparse import ArgumentParser


def parse_args():
    args = ArgumentParser()
    args.add_argument("file_name", help="")
    return args.parse_args()


if __name__ == "__main__":
    args = parse_args()
    pass
