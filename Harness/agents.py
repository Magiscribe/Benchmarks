"""Agent CLI registry and invocation.

Adding a new agent means adding one entry to AGENT_COMMANDS. No task code changes.
"""
import os
import subprocess
import sys


DEFAULT_BOOTSTRAP_PROMPT = """You are an autonomous agent. Your current working directory contains a file
named task.md. Read it and complete the task it describes.

Follow all constraints in task.md, including how to signal completion. Do not
ask clarifying questions — do the work. When you believe you are done, create
the .done file as task.md instructs and exit.
"""


# Each factory receives (prompt, model) and returns (argv, stdin_input).
# If stdin_input is not None, it's piped to the process (avoids Windows
# shell-quoting issues with multi-line prompts).
AGENT_COMMANDS = {
    "gemini": lambda prompt, model: ([
        "gemini", "--yolo",
        "-m", model or os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview"),
        "-p", prompt,
    ], None),
    "claude": lambda prompt, model: ([
        "claude", "--dangerously-skip-permissions",
        "--model", model or os.environ.get("CLAUDE_MODEL", "sonnet"),
        "-p",
    ], prompt),
    "codex": lambda prompt, model: ([
        "codex", "exec",
        "-m", model or os.environ.get("CODEX_MODEL", "gpt-5.4"),
        "--dangerously-bypass-approvals-and-sandbox", "-",
    ], prompt),
}


def available_agents():
    return sorted(AGENT_COMMANDS.keys())


def _prepare_env(agent: str, log):
    env = os.environ.copy()
    if agent == "gemini" and "GEMINI_API_KEY" not in env:
        gkey = env.get("GOOGLE_API_KEY")
        if gkey:
            env["GEMINI_API_KEY"] = gkey
            log("Set GEMINI_API_KEY from GOOGLE_API_KEY.")
        else:
            log("WARNING: Neither GEMINI_API_KEY nor GOOGLE_API_KEY is set.")
    return env


def invoke_agent(agent: str, model, prompt: str, cwd: str, timeout, log) -> int:
    """Run the agent CLI, blocking until it exits or `timeout` seconds elapse.

    Returns the process exit code (124 on timeout).
    """
    cmd, stdin_input = AGENT_COMMANDS[agent](prompt, model)
    env = _prepare_env(agent, log)

    log(f"Invoking agent: {' '.join(cmd[:3])}...")
    if timeout:
        log(f"(Timeout: {timeout}s. Will score on expiry.)")
    log("(Blocking until the agent CLI exits. Hit Ctrl+C to abort.)")

    popen_kwargs = dict(
        cwd=cwd,
        env=env,
        shell=(sys.platform == "win32"),
    )
    if stdin_input:
        popen_kwargs["stdin"] = subprocess.PIPE

    try:
        proc = subprocess.Popen(cmd, **popen_kwargs)
        if stdin_input:
            proc.stdin.write(stdin_input.encode("utf-8"))
            proc.stdin.close()
        return proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        log(f"Timeout of {timeout}s reached. Killing agent process...")
        proc.kill()
        proc.wait()
        return 124
