import ast
import os
import sys
from types import FrameType
from typing import Dict, List, Optional, Set

import typer

app = typer.Typer()

def run_with_trace(filepath: str) -> Set[str]:
    """Trace the execution of the given script and collect called functions."""
    traced_functions: Set[str] = set()

    def tracer(frame: FrameType, event: str, arg: Optional[object]) -> Optional[object]:
        if event == "call":
            code = frame.f_code
            module = frame.f_globals.get("__name__")
            func_name = code.co_name
            if module and func_name:
                traced_functions.add(f"{module}.{func_name}")
        return tracer

    sys.setprofile(tracer)
    try:
        with open(filepath) as f:
            code = compile(f.read(), filepath, 'exec')
            globals_dict = {"__name__": "__main__"}
            exec(code, globals_dict)
    finally:
        sys.setprofile(None)

    return traced_functions

def find_function_usage_in_file(
    filepath: str,
    target_module: str,
    target_function: str,
    imported_names: Optional[Dict[str, str]] = None,
    visited_funcs: Optional[Set[str]] = None,
) -> bool:
    """
    Analyze a single Python file AST to find if target_function from target_module
    is used directly or transitively.

    This is a basic implementation that:
    - Tracks imports to resolve names
    - Checks function calls
    - Checks simple function wrappers in the same file
    """
    if imported_names is None:
        imported_names = {}
    if visited_funcs is None:
        visited_funcs = set()

    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)

    # Map function names to their ast.FunctionDef nodes
    functions: Dict[str, ast.FunctionDef] = {}

    class FuncVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            functions[node.name] = node
            self.generic_visit(node)

    FuncVisitor().visit(tree)

    def is_target_call(node: ast.AST) -> bool:
        if not isinstance(node, ast.Call):
            return False

        func = node.func
        parts: List[str] = []
        while isinstance(func, ast.Attribute):
            parts.insert(0, func.attr)
            func = func.value

        if isinstance(func, ast.Name):
            parts.insert(0, func.id)

        full_call = ".".join(parts)
        target_full = f"{target_module}.{target_function}"

        return full_call == target_full

    def calls_target_or_transitive(
        func_node: ast.FunctionDef, call_stack: Optional[Set[str]] = None
    ) -> bool:
        if call_stack is None:
            call_stack = set()
        if func_node.name in call_stack:
            return False  # avoid recursion loops
        call_stack.add(func_node.name)

        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if is_target_call(node):
                    return True
                # Check if the call is to a local function: then recurse
                if isinstance(node.func, ast.Name):
                    fname = node.func.id
                    if fname in functions and fname not in call_stack:
                        if calls_target_or_transitive(functions[fname], call_stack):
                            return True
        return False

    # Process imports to fill imported_names
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    imported_names[alias.asname] = alias.name
                else:
                    imported_names[alias.name] = alias.name
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            for alias in node.names:
                full_name = f"{module}.{alias.name}" if module else alias.name
                if alias.asname:
                    imported_names[alias.asname] = full_name
                else:
                    imported_names[alias.name] = full_name

    # Search top-level calls and functions for usage
    for node in ast.walk(tree):
        # Check calls in global scope
        if isinstance(node, ast.Call):
            if is_target_call(node):
                return True
        # Check function wrappers
        if isinstance(node, ast.FunctionDef):
            if calls_target_or_transitive(node):
                return True

    return False

@app.command()
def check_usage(
    path: str = typer.Argument(..., help="Directory or file path to scan"),
    module: str = typer.Argument(..., help="Module name e.g. 'os.path'"),
    function: str = typer.Argument(..., help="Function name e.g. 'join'"),
    runtime: bool = typer.Option(False, "--runtime", help="Use runtime tracing")
) -> None:

    """
    Check whether Python files under PATH use FUNCTION from MODULE, directly or
    transitively.
    """
    matches: List[str] = []
    if os.path.isfile(path):
        files_to_check = [path]
    else:
        files_to_check = []
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(".py"):
                    files_to_check.append(os.path.join(root, file))

    for file in files_to_check:
        try:
            if runtime:
                called_funcs = run_with_trace(file)
                if f"{module}.{function}" in called_funcs:
                    matches.append(file)
            else:
                if find_function_usage_in_file(file, module, function):
                    matches.append(file)
        except Exception as e:
            typer.echo(f"Error processing {file}: {e}")

    if matches:
        typer.echo(f"Found usage of {module}.{function} in:")
        for m in matches:
            typer.echo(f" - {m}")
        raise typer.Exit(code=0)
    else:
        typer.echo(f"No usage of {module}.{function} found under {path}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
