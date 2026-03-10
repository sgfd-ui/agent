from app.flow.graph import build_graph


def main() -> None:
    """AutoVideoMiner entrypoint."""
    graph = build_graph()
    print("Graph initialized:", graph)


if __name__ == "__main__":
    main()
