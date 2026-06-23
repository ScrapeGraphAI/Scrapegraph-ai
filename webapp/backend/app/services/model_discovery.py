import subprocess

from . import logging_service

LOG = "model_discovery"


def discover_ollama_models() -> list[str]:
    logging_service.debug(LOG, "Discovering local ollama models")
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode != 0:
            logging_service.warning(LOG, f"ollama list exited with code {result.returncode}: {result.stderr.strip()}")
            return []

        lines = result.stdout.strip().splitlines()
        if len(lines) < 2:  # noqa: PLR2004
            return []

        models = []
        for line in lines[1:]:
            parts = line.split()
            if parts:
                name = parts[0].rstrip("/")
                models.append(name)

        logging_service.info(LOG, f"Discovered {len(models)} ollama models")
        logging_service.debug(LOG, f"Models: {models}")
        return sorted(models)

    except FileNotFoundError:
        logging_service.warning(LOG, "ollama binary not found in PATH")
        return []
    except subprocess.TimeoutExpired:
        logging_service.warning(LOG, "ollama list timed out after 5s")
        return []
