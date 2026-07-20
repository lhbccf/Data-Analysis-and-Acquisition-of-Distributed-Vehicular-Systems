import importlib.util
import json
import tempfile
from pathlib import Path


TEST_SCRIPT = Path(__file__).parent / "integration" / "test_nextion.py"


def load_nextion_test_module():
    spec = importlib.util.spec_from_file_location("integration_test_nextion", TEST_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_manual_nextion_test_passes_complete_worker_config():
    module = load_nextion_test_module()

    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "nextion_port": "/dev/configured",
                    "nextion_baud": 115200,
                    "redline": 8000,
                    "shift_point": 7000,
                    "nextion_sessions_limit": 3,
                }
            ),
            encoding="utf-8",
        )

        config = module.read_config_from_args(
            ["test_nextion.py", "/dev/override", "9600"], config_path
        )

    assert config["nextion_port"] == "/dev/override"
    assert config["nextion_baud"] == 9600
    assert config["redline"] == 8000
    assert config["shift_point"] == 7000
    assert config["nextion_sessions_limit"] == 3
