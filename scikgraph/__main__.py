"""Entry point for `python -m scikgraph` and the `scikgraph` console script."""
import argparse
import os

from waitress import serve

from scikgraph import create_app


def main():
    parser = argparse.ArgumentParser(
        prog="scikgraph",
        description="Run the SciKGraph web application.",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Bind address (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("SCIKGRAPH_PORT", "8080")),
        help="Bind port (default: 8080, override with $SCIKGRAPH_PORT)",
    )
    args = parser.parse_args()

    app = create_app()
    print("SciKGraph serving on http://{}:{}/".format(args.host, args.port))
    serve(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
