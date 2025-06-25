import ast
import re
from pathlib import Path
from typing import Tuple, List, Optional
from radon.visitors import ComplexityVisitor
from radon.metrics import h_visit_ast # Halstead metrics, could be useful later
from radon.raw import analyze as analyze_raw # Raw metrics like SLOC, LLOC

class CodeStructureValidator:
    MIN_NON_EMPTY_LINES = 10  # Heuristic for non-trivial code
    MIN_STATEMENTS = 5       # Another heuristic: expecting at least a few logical statements
    MAX_AVG_COMPLEXITY = 7   # Average cyclomatic complexity per function/method
    MAX_FUNCTION_COMPLEXITY = 15 # Max cyclomatic complexity for any single function/method

    def __init__(self, code_content: str, filepath: Optional[Path] = None):
        self.code_content = code_content
        self.tree = None
        try:
            self.tree = ast.parse(self.code_content)
        except SyntaxError as e:
            self.tree = None # Will be handled by check_non_trivial or other AST-based checks
            # self.errors.append(f"Initial AST parsing failed: {e}") # Already handled by syntax audit
            pass # Syntax errors should be caught by the syntax auditor first.
        self.filepath = filepath # Optional, mainly for context in messages
        self.lines = [line for line in code_content.splitlines()]
        self.errors: List[str] = []
        self.is_script_intent = True # Default assumption, can be refined if more context is passed

        # Basic check: if filepath suggests a specific entry point name like main.py
        if self.filepath and self.filepath.name.lower() != "main.py" and \
           self.filepath.name.lower() != "app.py": # Common entry point names
            # Could potentially set self.is_script_intent = False if it's clearly a library module
            pass


    def _is_comment_or_empty(self, line: str) -> bool:
        stripped_line = line.strip()
        return not stripped_line or stripped_line.startswith("#")

    def check_non_trivial(self) -> bool:
        non_empty_lines = [line for line in self.lines if not self._is_comment_or_empty(line)]
        if len(non_empty_lines) < self.MIN_NON_EMPTY_LINES:
            self.errors.append(
                f"Code seems too trivial: less than {self.MIN_NON_EMPTY_LINES} non-empty/non-comment lines "
                f"(found {len(non_empty_lines)})."
            )
            return False

        # Check for some minimal number of statements using AST
        try:
            tree = ast.parse(self.code_content)
            statement_count = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
                                     ast.If, ast.For, ast.AsyncFor, ast.While,
                                     ast.With, ast.AsyncWith, ast.Try, ast.Assign,
                                     ast.Expr, ast.Return, ast.Raise, ast.Assert)):
                    statement_count += 1

            if statement_count < self.MIN_STATEMENTS:
                 self.errors.append(
                    f"Code seems too trivial: less than {self.MIN_STATEMENTS} significant AST statements "
                    f"(found {statement_count})."
                )
                 return False

        except SyntaxError as e:
            # This shouldn't happen if syntax audit already passed, but as a safeguard
            self.errors.append(f"Syntax error during non-trivial check (AST parsing): {e}")
            return False
        return True

    def check_entry_point(self) -> bool:
        if not self.is_script_intent: # If determined not to be a script, skip this check
            return True

        # Regex to find 'if __name__ == "__main__":'
        # Accounts for variations in spacing and quotes.
        entry_point_pattern = re.compile(r"""
            if\s+__name__\s*==\s*                      # if __name__ ==
            (?:
                "__main__"                             # "__main__"
                |
                '__main__'                             # '__main__'
            )
            \s*:                                       # :
        """, re.VERBOSE)

        found_entry_point = False
        for line in self.lines:
            if entry_point_pattern.search(line):
                found_entry_point = True
                break

        if not found_entry_point:
            self.errors.append(
                "No clear script entry point found (expected 'if __name__ == \"__main__\":')."
            )
            return False
        return True

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Runs all structure validations.
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_error_messages)
        """
        self.errors = [] # Reset errors for this validation run

        is_valid = self.check_non_trivial()
        # Only check for entry point if non-trivial check passes,
        # or if script_intent is True (could be a tiny valid script)
        if self.is_script_intent : # For now, always check entry point if it's a script
             is_valid = self.check_entry_point() and is_valid # Combine with previous is_valid

        return is_valid, self.errors

def validate_code_structure(code_content: str, filepath: Optional[Path] = None) -> Tuple[bool, List[str]]:
    """
    Convenience function to use the CodeStructureValidator.
    """
    validator = CodeStructureValidator(code_content, filepath)
    return validator.validate()

def run_flake8_validation(filepath: Path) -> Tuple[bool, List[str]]:
    """
    Runs flake8 on the given file and returns success/failure and errors.
    """
    import subprocess
    import logging # Add logging for this function
    logger = logging.getLogger(__name__)

    if not filepath.exists() or not filepath.is_file():
        return False, [f"File not found for flake8 validation: {filepath}"]

    try:
        # Using the .venv python's flake8 module ensures it's the one from our environment
        # This is more robust than relying on a globally available flake8
        # Adjust path to python executable if .venv is not always in root or named differently
        # For sandbox, assume .venv/bin/python is correct relative to execution dir
        # If WorkshopManager runs from repo root, this should be fine.
        # A more robust way might be sys.executable if this validator is always run in same venv
        # as WorkshopManager. For now, assume .venv is accessible.

        # Path to flake8 within the virtual environment
        # This assumes the script running this (e.g. WorkshopManager) is in the project root
        # and .venv is also in the project root.
        # If this code is part of a library used elsewhere, this path might need to be more dynamic.
        # For now, let's assume direct execution context.

        # To make it more portable, we can try to find flake8 in PATH first,
        # or use `python -m flake8`. Let's use `python -m flake8`.
        # This requires flake8 to be installed in the python environment being used.

        # Determine the python executable from the current environment
        python_executable = Path(subprocess.check_output(["which", "python"], text=True).strip())
        # If running in .venv, this should point to .venv/bin/python
        # More robust: use sys.executable if this module is guaranteed to run in the target venv
        # For now, this is a common approach.
        # python_executable = ".venv/bin/python" # Less robust if .venv is not in CWD

        flake8_command = [
            str(python_executable), # Use the determined python executable
            "-m", "flake8",
            str(filepath)
        ]

        logger.info(f"Running flake8 command: {' '.join(flake8_command)}")
        process = subprocess.run(flake8_command, capture_output=True, text=True, check=False) # check=False to handle non-zero exits ourselves

        if process.returncode == 0 and not process.stdout.strip():
            # Flake8 found no issues if stdout is empty and return code is 0
            # Some versions of flake8 might return 0 even with warnings if not configured to error on them.
            # However, typically, any output to stdout means issues were found.
            # A stricter check might be just `process.returncode == 0`.
            # For now, let's consider any stdout as potential issues to report.
            return True, []
        else:
            # If stdout is not empty, or returncode is non-zero, there are issues.
            # Flake8 outputs errors/warnings to stdout.
            # Stderr might contain other execution errors of flake8 itself.
            errors = process.stdout.strip().splitlines()
            if process.stderr.strip(): # Log flake8's own errors if any
                logger.warning(f"Flake8 stderr output: {process.stderr.strip()}")
                # Optionally add stderr to returned errors if it's relevant to code quality
                # errors.append(f"Flake8 execution error: {process.stderr.strip()}")

            # Ensure we return False if there was any output, even if returncode was 0 (e.g. only warnings)
            if errors:
                return False, errors
            elif process.returncode != 0: # No stdout, but non-zero exit (less common for flake8)
                return False, [f"flake8 exited with code {process.returncode} but no specific errors on stdout. Stderr: {process.stderr.strip()}"]
            else: # Should ideally not be reached if logic above is sound (returncode 0, no stdout = success)
                 return True, []


    except FileNotFoundError: # If `python` or `flake8` (if not using -m) isn't found
        logger.error("flake8 command not found. Ensure flake8 is installed and in PATH or python -m flake8 works.", exc_info=True)
        return False, ["flake8 execution failed: command not found. Is it installed in the environment?"]
    except subprocess.CalledProcessError as e: # Should be caught by check=False now
        logger.error(f"flake8 execution failed with CalledProcessError: {e}", exc_info=True)
        errors = e.stdout.strip().splitlines() if e.stdout else []
        if e.stderr:
            errors.extend(e.stderr.strip().splitlines())
        if not errors:
            errors = [str(e)]
        return False, errors
    except Exception as e:
        logger.error(f"An unexpected error occurred during flake8 validation: {e}", exc_info=True)
        return False, [f"Unexpected error during flake8: {str(e)}"]
