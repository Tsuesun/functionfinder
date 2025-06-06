# FunctionFinder

**FunctionFinder** is a command-line tool for statically analyzing Python code to detect whether a specific function from a library is being used — either directly or indirectly (transitive support coming soon).

## 🔍 What It Does

Given a target directory and a fully qualified function (e.g. `os.path.join`), FunctionFinder will scan all `.py` files under that directory and report whether the function is used.

## ✨ Features

- 📂 Recursively scans Python files in a given directory
- 🧠 Parses code using Python's `ast` module for safe static analysis
- ✅ Detects direct calls to a specified function (e.g. `os.path.join`)
- 🧪 Includes a test suite using `pytest`
- 🚀 Built as a CLI with `typer`
- 🔜 Transitive usage detection (e.g. functions used within `requests`) — *coming soon*

## 🚀 Installation

You can run the project using [`uv`](https://github.com/astral-sh/uv) for fast virtualenv & dependency management:

```bash
uv venv
source .venv/bin/activate
uv pip install -e .[dev]
```

## 🛠️ Usage

```bash
functionfinder <path-to-directory> <module> <function>
```

### Example

```bash
functionfinder ./tests os.path join
```

Output:

```
✅ Found usage of os.path.join in: tests/test_script.py
```

## 🧪 Running Tests

```bash
uv run pytest
```

## 📦 Project Structure

```
functionfinder/
├── functionfinder/
│   └── main.py        # CLI logic and function detection
├── tests/
│   └── test_usage_check.py
├── pyproject.toml     # Dependencies and CLI entrypoint
└── README.md
```

## ✅ Roadmap

- [x] Direct function usage detection
- [ ] Transitive usage detection via runtime tracing
- [ ] Support for multiple functions/modules at once
- [ ] JSON output for integration with tooling
- [ ] Optional ignore list (e.g., skip test files)

## 📝 License

MIT License

Copyright (c) 2025 Tsuesun

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.