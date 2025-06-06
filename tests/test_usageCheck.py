import os
import tempfile
from typer.testing import CliRunner
from functionfinder.main import app

runner = CliRunner()

def write_script(path: str, content: str):
    with open(path, "w") as f:
        f.write(content)

def test_direct_usage_detection():
    with tempfile.TemporaryDirectory() as tmpdir:
        script = os.path.join(tmpdir, "direct.py")
        write_script(script, "import os\nos.path.join('a', 'b')\n")
        result = runner.invoke(app, [tmpdir, "os.path", "join"])
        print(result.output)
        assert result.exit_code == 0
        assert "direct.py" in result.output

def test_transitive_usage_detection():
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

def test_no_usage():
    with tempfile.TemporaryDirectory() as tmpdir:
        script = os.path.join(tmpdir, "no_use.py")
        write_script(script, "print('hello world')\n")
        result = runner.invoke(app, [tmpdir, "os.path", "join"])
        assert result.exit_code == 1
        assert "No usage" in result.output
