# code_summarizer/rule_based_navigator.py

import inspect

# This is your smart_complete_code function, unchanged.
def smart_complete_code(code_input: str) -> str:
    lines = code_input.strip().split("\n")
    completed_lines = []
    for line in lines:
        stripped = line.strip()
        indent = " " * (len(line) - len(line.lstrip()) + 4)
        if stripped.startswith(("def ", "for ", "while ", "if ")) and not stripped.endswith(":"):
            line += ":"
        completed_lines.append(line)
        if stripped.startswith("def "):
            func_name = stripped[4:].split("(")[0].strip()
            if "fib" in func_name.lower():
                completed_lines.append(f"{indent}seq = [0, 1]")
                completed_lines.append(f"{indent}for i in range(2, n):")
                completed_lines.append(f"{indent}    seq.append(seq[i-1] + seq[i-2])")
                completed_lines.append(f"{indent}return seq")
            else:
                completed_lines.append(f"{indent}# Auto-completed function body")
                completed_lines.append(f"{indent}return None")
        elif stripped.startswith(("for ", "if ")):
            completed_lines.append(f"{indent}pass")
        elif stripped.startswith("while "):
            completed_lines.append(f"{indent}break")
    return "\n".join(completed_lines)

# This is your make_example_args function, unchanged.
def make_example_args(sig: inspect.Signature):
    args = []
    for name, param in sig.parameters.items():
        if name == 'self':
            continue
        if param.default is not inspect.Parameter.empty:
            args.append(param.default)
            continue
        lname = name.lower()
        if 'name' in lname or 'text' in lname:
            args.append("World")
        elif 'count' in lname or 'n' == lname or 'num' in lname:
            args.append(5)
        elif 'list' in lname or 'items' in lname:
            args.append([1, 2, 3])
        else:
            args.append(None)
    return args

def navigate_and_run(incomplete_code):
    """
    A generator function that completes, executes, and demonstrates code,
    yielding its output for display in Streamlit.
    """
    # 1. Complete the code
    yield "### ✅ Completed Code:\n"
    completed_code = smart_complete_code(incomplete_code)
    yield f"```python\n{completed_code}\n```"

    # 2. Execute the completed code
    yield "\n### 💻 Executing Completed Code...\n"
    exec_globals = {}
    try:
        exec(completed_code, exec_globals)
        yield "Execution finished."
    except Exception as e:
        yield f"⚠️ Error during execution: {e}"
        return

    # 3. Find and demonstrate user-defined functions
    user_funcs = {name: val for name, val in exec_globals.items() if inspect.isfunction(val)}
    if user_funcs:
        yield "\n### 🔎 Detected Functions - Attempting Demo Calls...\n"
        for fname, func in user_funcs.items():
            try:
                sig = inspect.signature(func)
                example_args = make_example_args(sig)
                yield f"\n▶ **Calling `{fname}` with guessed args: `{example_args}`**"
                result = func(*example_args)
                yield f"&nbsp;&nbsp;↳ `{fname}` returned: `{result}`"
            except Exception as e:
                yield f"&nbsp;&nbsp;⚠️ Calling `{fname}` raised an error: {e}"
    
    yield "\n### ✅ Done."