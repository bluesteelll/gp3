from graph.builder import build_graph
from session import create_session, load_long_term_memory


def main():
    session_id, session_dir = create_session()
    memory = load_long_term_memory()

    app = build_graph()
    result = app.invoke({
        "messages": [],
        "session_id": session_id,
        "session_dir": str(session_dir),
        "session_log": [],
        "code_outputs": [],
        "notes": {},
        "long_term_memory": {"history": memory},
        "retry_count": 0,
    })
    print(f"Session: {session_id}")
    print(result)


main()
