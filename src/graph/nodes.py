import re

from workflow import agents


NOTE_PATTERN = re.compile(r"NOTE FOR (\w+):\s*(.+?)(?=NOTE FOR |\Z)", re.DOTALL)


def extract_notes(text):
    return {target.strip(): msg.strip() for target, msg in NOTE_PATTERN.findall(text)}


def incoming_note(state, agent_name):
    return state.get("notes", {}).get(agent_name, "")


def compose_task(base_task, note):
    if not note:
        return base_task
    return f"Notes from prior agents:\n{note}\n\n---\n\n{base_task}"


def run_agent(name, task):
    result = agents[name].invoke({"messages": [("user", task)]})
    final = result["messages"][-1].content
    return result["messages"], final


def collector_node(state):
    session_dir = state["session_dir"]
    raw_path = f"{session_dir}/raw/dataset.csv"

    task = compose_task(
        f"Collect a dataset for ML training and save it to: {raw_path}",
        incoming_note(state, "data_collector"),
    )
    messages, final = run_agent("data_collector", task)

    return {
        "messages": messages,
        "dataset_path": raw_path,
        "notes": extract_notes(final),
        "session_log": state.get("session_log", []) + ["collector: raw data saved"],
    }


def preprocessor_node(state):
    session_dir = state["session_dir"]
    raw_path = state["dataset_path"]
    processed_path = f"{session_dir}/processed/clean.csv"

    task = compose_task(
        f"Raw dataset: {raw_path}\nClean it and save the processed version to: {processed_path}",
        incoming_note(state, "data_preprocessor"),
    )
    messages, final = run_agent("data_preprocessor", task)

    return {
        "messages": messages,
        "dataset_path": processed_path,
        "preprocessing_info": {"summary": final},
        "notes": extract_notes(final),
        "session_log": state.get("session_log", []) + ["preprocessor: cleaned"],
    }


def validator_node(state):
    session_dir = state["session_dir"]
    dataset_path = state["dataset_path"]
    report_path = f"{session_dir}/reports/validation.json"

    task = compose_task(
        f"Dataset to validate: {dataset_path}\nSave the validation report to: {report_path}",
        incoming_note(state, "data_validator"),
    )
    messages, final = run_agent("data_validator", task)
    passed = "VERDICT: pass" in final

    return {
        "messages": messages,
        "error": None if passed else final,
        "notes": extract_notes(final),
        "session_log": state.get("session_log", []) + [f"validator: {'pass' if passed else 'fail'}"],
    }


def analyzer_node(state):
    session_dir = state["session_dir"]
    dataset_path = state["dataset_path"]
    report_path = f"{session_dir}/reports/analysis.json"

    task = compose_task(
        f"Dataset to analyze: {dataset_path}\nSave the analysis report to: {report_path}",
        incoming_note(state, "data_analyzer"),
    )
    messages, final = run_agent("data_analyzer", task)

    return {
        "messages": messages,
        "dataset_info": {"summary": final},
        "notes": extract_notes(final),
        "session_log": state.get("session_log", []) + ["analyzer: done"],
    }


def trainer_node(state):
    session_dir = state["session_dir"]
    dataset_path = state["dataset_path"]
    model_path = f"{session_dir}/models/model.pkl"

    task = compose_task(
        f"Training dataset: {dataset_path}\nSave the trained model to: {model_path}",
        incoming_note(state, "trainer"),
    )
    messages, final = run_agent("trainer", task)

    return {
        "messages": messages,
        "best_model_name": "model.pkl",
        "training_results": {"summary": final},
        "notes": extract_notes(final),
        "session_log": state.get("session_log", []) + ["trainer: model saved"],
    }


def reviser_node(state):
    session_dir = state["session_dir"]
    dataset_path = state["dataset_path"]
    model_path = f"{session_dir}/models/{state.get('best_model_name', 'model.pkl')}"
    eval_path = f"{session_dir}/reports/evaluation.json"

    task = compose_task(
        f"Model to evaluate: {model_path}\nTest dataset: {dataset_path}\nSave the evaluation report to: {eval_path}",
        incoming_note(state, "model_reviser"),
    )
    messages, final = run_agent("model_reviser", task)

    return {
        "messages": messages,
        "metrics": {"summary": final},
        "session_log": state.get("session_log", []) + ["reviser: evaluated"],
    }
