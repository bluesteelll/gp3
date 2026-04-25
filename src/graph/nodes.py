import json
from datetime import datetime
from pathlib import Path

from session import (
    append_to_long_term_memory,
    save_conversations,
    session_paths,
    update_meta,
)
from workflow import agents


MARKER = "AGENT_RESULT_DATA:"


def parse_final_result(text):
    idx = text.rfind(MARKER)
    if idx == -1:
        return {}
    payload = text[idx + len(MARKER):].strip()
    if payload.startswith("```"):
        payload = payload.strip("`").strip()
        if payload.lower().startswith("json"):
            payload = payload[4:].strip()
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return {}


def incoming_note(state, agent_name):
    return state.get("notes", {}).get(agent_name, "")


def compose_task(base_task, note):
    if not note:
        return base_task
    return f"Notes from prior agents:\n{note}\n\n---\n\n{base_task}"


def info_from_result(result, fallback_text):
    payload = {k: v for k, v in result.items() if k != "notes"}
    return payload or {"summary": fallback_text}


def run_agent(name, task):
    response = agents[name].invoke({"messages": [("user", task)]})
    messages = response["messages"]
    final = messages[-1].content
    return messages, final, parse_final_result(final)


def collector_node(state):
    paths = session_paths(state["session_dir"])
    raw_path = paths["raw_data"]

    task = compose_task(
        f"Collect a dataset for ML training and save it to: {raw_path}",
        incoming_note(state, "data_collector"),
    )
    messages, final, result = run_agent("data_collector", task)

    return {
        "messages": messages,
        "dataset_path": str(raw_path),
        "notes": result.get("notes", {}),
        "session_log": ["collector: raw data saved"],
    }


def preprocessor_node(state):
    paths = session_paths(state["session_dir"])
    raw_path = state["dataset_path"]
    processed_path = paths["processed_data"]

    task = compose_task(
        f"Raw dataset: {raw_path}\nClean it and save the processed version to: {processed_path}",
        incoming_note(state, "data_preprocessor"),
    )
    messages, final, result = run_agent("data_preprocessor", task)

    return {
        "messages": messages,
        "dataset_path": str(processed_path),
        "preprocessing_info": info_from_result(result, final),
        "notes": result.get("notes", {}),
        "session_log": ["preprocessor: cleaned"],
    }


def validator_node(state):
    paths = session_paths(state["session_dir"])
    dataset_path = state["dataset_path"]
    report_path = paths["validation_report"]

    task = compose_task(
        f"Dataset to validate: {dataset_path}\nSave the validation report to: {report_path}",
        incoming_note(state, "data_validator"),
    )
    messages, final, result = run_agent("data_validator", task)
    verdict = result.get("verdict", "")
    passed = verdict == "pass"

    return {
        "messages": messages,
        "error": None if passed else (result.get("summary") or final),
        "notes": result.get("notes", {}),
        "session_log": [f"validator: {verdict or 'unknown'}"],
    }


def analyzer_node(state):
    paths = session_paths(state["session_dir"])
    dataset_path = state["dataset_path"]
    report_path = paths["analysis_report"]

    task = compose_task(
        f"Dataset to analyze: {dataset_path}\nSave the analysis report to: {report_path}",
        incoming_note(state, "data_analyzer"),
    )
    messages, final, result = run_agent("data_analyzer", task)

    return {
        "messages": messages,
        "dataset_info": info_from_result(result, final),
        "notes": result.get("notes", {}),
        "session_log": ["analyzer: done"],
    }


def trainer_node(state):
    paths = session_paths(state["session_dir"])
    dataset_path = state["dataset_path"]
    model_path = paths["model"]

    task = compose_task(
        f"Training dataset: {dataset_path}\nSave the trained model to: {model_path}",
        incoming_note(state, "trainer"),
    )
    messages, final, result = run_agent("trainer", task)

    return {
        "messages": messages,
        "best_model_name": result.get("model_name", "model.pkl"),
        "training_results": info_from_result(result, final),
        "notes": result.get("notes", {}),
        "session_log": ["trainer: model saved"],
    }


def reviser_node(state):
    paths = session_paths(state["session_dir"])
    dataset_path = state["dataset_path"]
    model_path = paths["model_dir"] / state.get("best_model_name", "model.pkl")
    eval_path = paths["evaluation_report"]

    task = compose_task(
        f"Model to evaluate: {model_path}\nTest dataset: {dataset_path}\nSave the evaluation report to: {eval_path}",
        incoming_note(state, "model_reviser"),
    )
    messages, final, result = run_agent("model_reviser", task)

    return {
        "messages": messages,
        "metrics": info_from_result(result, final),
        "notes": result.get("notes", {}),
        "session_log": [f"reviser: {result.get('verdict', 'unknown')}"],
    }


def summarizer_node(state):
    session_id = state["session_id"]
    session_dir = Path(state["session_dir"])
    paths = session_paths(session_dir)
    conversations_path = save_conversations(session_dir, state["messages"])
    summary_path = paths["summary"]

    task = compose_task(
        f"Read the agent conversations from: {conversations_path}\n"
        f"Write a concise markdown summary of this pipeline run to: {summary_path}",
        incoming_note(state, "summarizer"),
    )
    messages, final, result = run_agent("summarizer", task)

    append_to_long_term_memory({
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "summary_path": str(summary_path),
    })
    update_meta(session_dir, summary_path=str(summary_path), status="completed")

    return {
        "messages": messages,
        "session_log": ["summarizer: done"],
    }
