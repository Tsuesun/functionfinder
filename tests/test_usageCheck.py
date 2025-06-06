import os
import tempfile
from typer.testing import CliRunner
from functionfinder.main import app

runner = CliRunner()

def write_script(path: str, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)

def test_direct_usage_detection() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        script = os.path.join(tmpdir, "direct.py")
        write_script(script, "import os\nos.path.join('a', 'b')\n")
        result = runner.invoke(app, [tmpdir, "os.path", "join"])
        print(result.output)
        assert result.exit_code == 0
        assert "direct.py" in result.output

def test_transitive_usage_detection() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        script = os.path.join(tmpdir, "transitive.py")
        write_script(script, """
import os

def helper():
    return os.path.join("x", "y")

def main():
    return helper()

main()
""")
        result = runner.invoke(app, [tmpdir, "os.path", "join"])
        assert result.exit_code == 0
        assert "transitive.py" in result.output

def test_no_usage() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        script = os.path.join(tmpdir, "no_use.py")
        write_script(script, "print('hello world')\n")
        result = runner.invoke(app, [tmpdir, "os.path", "join"])
        assert result.exit_code == 1
        assert "No usage" in result.output

def test_runtime_tracing_detects_transitive_import() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "uses_requests.py")
        script_content = """
import requests
requests.get("https://example.com/path?query=1")
"""
        write_script(script_path, script_content)

        result = runner.invoke(app, [script_path, "urllib.parse", "urlparse", "--runtime"])
        print(result.output)
        assert result.exit_code == 0
        assert "urllib.parse.urlparse" in result.output