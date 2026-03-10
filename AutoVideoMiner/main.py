from app.flow.graph import build_graph, run_cycle


def main() -> None:
    """AutoVideoMiner entrypoint."""
    runtime = build_graph()
    state = run_cycle(runtime)
    print("Graph next state:", state.get("next"))


if __name__ == "__main__":
    main()
