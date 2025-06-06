import ast
import os
from typing import Optional, List

import typer

app = typer.Typer()

def calls_target_or_transitive(
    func_node: ast.FunctionDef,
    target_module: str,
    target_function: str,
    call_stack: Optional[List[ast.FunctionDef]] = None
) -> bool:
    """
    Recursively check if the given function node calls the target function
    directly or indirectly (transitive).

    Args:
        func_node: AST node of the function definition to analyze.
        target_module: The module name to match, e.g. 'os.path'.
        target_function: The function name to match, e.g. 'join'.
        call_stack: List of previously visited functions to avoid cycles.

    Returns:
        True if target function is called directly or indirectly.
    """
    if call_stack is None:
        call_stack = []

    if func_node in call_stack:
        return False  # Avoid recursion cycles

    call_stack.append(func_node)

    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            # Example: check if the call matches the target function
            # This part depends on how you resolve the function call fully
            if is_target_call(node, target_module, target_function):
                return True
            # If call is to another function defined in the code,
            # you could recursively check that function here.
            # (This requires you to map call names to func_nodes)
            # Example recursive call omitted here for brevity.

    call_stack.pop()
    return False

def is_target_call(node: ast.Call, target_module: str, target_function: str) -> bool:
    """
    Check if an AST Call node corresponds to the target function call.

    Args:
        node: AST Call node.
        target_module: Target module name as string.
        target_function: Target function name as string.

    Returns:
        True if node matches target.
    """
    # Implementation depends on your import and usage analysis
    # Example simplified:
    if isinstance(node.func, ast.Attribute):
        if node.func.attr == target_function:
            # Further check if node.func.value corresponds to target_module
            # (e.g. 'os.path')
            # This can get complex and might need symbol resolution.
            return True
    elif isinstance(node.func, ast.Name):
        if node.func.id == target_function:
            # Might be direct import like `from os.path import join`
            return True
    return False

@app.command()
def main(
    directory: str,
    module: str,
    function: str,
) -> None:
    """
    CLI entrypoint. Scan directory for usage of module.function.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    source = f.read()
                tree = ast.parse(source, filename=filepath)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if calls_target_or_transitive(node, module, function):
                            typer.echo(f"✅ Found usage of {module}.{function} in: {filepath}")
                            return
    typer.echo(f"No usage of {module}.{function} found under {directory}")

if __name__ == "__main__":
    app()
