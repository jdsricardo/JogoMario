"""Atalho para o fluxo principal definido em app.py."""

from app import build_arg_parser, run_training


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    run_training(args)


if __name__ == "__main__":
    main()
