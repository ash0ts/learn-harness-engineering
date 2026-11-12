def evaluate(checks):
    """Your analysis is separate from the protected acceptance checks."""
    return {"checks_passed": sum(check["passed"] for check in checks),
            "checks_total": len(checks)}


def log_evaluation(run, metrics):
    # `run` is a real W&B run, created by the coordinator with a stable identity.
    run.log({"student/" + key: value for key, value in metrics.items()})
