"""Stage eval/ outside the task tree during agent runs so it can't be peeked."""
import shutil
import tempfile
from pathlib import Path


def stage_eval(eval_dir: Path, task_name: str) -> str:
    if not eval_dir.exists():
        raise RuntimeError(
            f"eval dir not found at {eval_dir}. If a prior run was interrupted, "
            "check `.harness_state.json` for `eval_staged_at` and restore manually."
        )
    staging_parent = Path(tempfile.mkdtemp(prefix=f"benchmark-eval-{task_name}-"))
    staged = staging_parent / "eval"
    shutil.move(str(eval_dir), str(staged))
    return str(staged)


def restore_eval(eval_dir: Path, staged_path_str: str, log):
    if not staged_path_str:
        return
    staged = Path(staged_path_str)
    if not staged.exists():
        log(f"WARNING: staged eval missing at {staged}. eval/ will not be restored.")
        return
    if eval_dir.exists():
        log(f"WARNING: {eval_dir} already exists; removing staged copy at {staged}.")
        shutil.rmtree(staged.parent)
        return
    shutil.move(str(staged), str(eval_dir))
    try:
        staged.parent.rmdir()
    except OSError:
        pass
