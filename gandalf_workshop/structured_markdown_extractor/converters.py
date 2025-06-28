import subprocess
import shutil
from typing import Optional

def convert_tex_to_markdown(tex_content: str) -> Optional[str]:
    """
    Converts LaTeX content to Markdown.
    Tries Pandoc first, then falls back to the 'latex2markdown-py' Python library.

    Args:
        tex_content: A string containing the LaTeX content.

    Returns:
        A string containing the converted Markdown content, or None if all conversion methods fail.
    """
    # Attempt 1: Use Pandoc
    pandoc_path = shutil.which("pandoc")
    if pandoc_path: # Check if pandoc is in PATH
        try:
            process = subprocess.run(
                [pandoc_path, "--from", "latex", "--to", "markdown_strict", "--wrap=none"],
                input=tex_content,
                text=True,
                capture_output=True,
                check=True,
                timeout=30
            )
            print("Successfully converted TeX to Markdown using Pandoc.")
            return process.stdout
        except FileNotFoundError: # Should not happen if shutil.which found it, but as a safeguard
            print("Pandoc reported by shutil.which but not found by subprocess. Proceeding to fallback.")
        except subprocess.CalledProcessError as e:
            print(f"Pandoc conversion failed with error: {e.stderr}")
        except subprocess.TimeoutExpired:
            print("Pandoc conversion timed out.")
        except Exception as e: # Catch other potential errors from Pandoc execution
            print(f"An unexpected error occurred while trying to use Pandoc: {e}")
    else:
        print("Pandoc executable not found in PATH.")

    # Attempt 2: Fallback to Python library (latex2markdown-py)
    print("Attempting fallback TeX to plain text conversion using 'pylatexenc' library...")
    try:
        from pylatexenc.latex2text import LatexNodes2Text
        from pylatexenc.latexwalker import LatexWalkerError

        # Convert LaTeX to plain text. This is often better for LLMs than raw LaTeX.
        # While not full Markdown, it preserves content and some structure.
        plain_text_content = LatexNodes2Text().latex_to_text(tex_content)

        print("Successfully converted TeX to plain text using 'pylatexenc' library.")
        # For the purpose of this tool, we are treating this plain text as a form of "markdown"
        # suitable for LLM processing, as it's cleaner than raw TeX.
        return plain_text_content

    except LatexWalkerError as e:
        print(f"Pylatexenc parsing error during fallback conversion: {e}")
        return None
    except ImportError:
        print("Python library 'pylatexenc' not installed or import failed. Cannot use Python fallback.")
        print("Please install it: pip install pylatexenc")
        return None
    except Exception as e:
        print(f"Python library 'pylatexenc' conversion failed: {e}")
        return None

if __name__ == '__main__':
    sample_tex_content = r"""
\documentclass{article}
\usepackage{amsmath}
\title{Test Document}
\author{Jules Verne}
\date{\today}
\begin{document}
\maketitle

\section{Introduction}
This is a test document. Here is an inline equation: $E = mc^2$.
And a display equation:
$$ \sum_{i=1}^{n} i = \frac{n(n+1)}{2} $$
Also, let's test some \textbf{bold} and \textit{italic} text.
\subsection{Subsection}
Itemize:
\begin{itemize}
    \item First item.
    \item Second item with $x_i$.
\end{itemize}
Enumerate:
\begin{enumerate}
    \item Step 1.
    \item Step 2.
\end{enumerate}
\end{document}
"""

    print("--- Testing TeX to Markdown Conversion ---")

    print("\n=== Scenario 1: Pandoc is available (simulated by default path check) ===")
    md_pandoc = convert_tex_to_markdown(sample_tex_content)
    if md_pandoc:
        print("\nPandoc Output:\n----------------\n", md_pandoc, "\n----------------")
    else:
        print("Pandoc conversion failed or Pandoc not available (or fallback also failed).")

    print("\n=== Scenario 2: Pandoc is NOT available (simulating by overriding shutil.which) ===")
    original_shutil_which = shutil.which
    def mock_shutil_which_pandoc_absent(cmd):
        if cmd == "pandoc":
            return None # Simulate pandoc not found
        return original_shutil_which(cmd)

    shutil.which = mock_shutil_which_pandoc_absent

    md_fallback = convert_tex_to_markdown(sample_tex_content)
    if md_fallback:
        print("\nPython Fallback Output (latex2markdown-py):\n----------------\n", md_fallback, "\n----------------")
    else:
        print("Python fallback conversion failed (latex2markdown-py not installed or error during conversion).")
        print("Make sure 'latex2markdown-py' is installed: pip install latex2markdown-py")

    shutil.which = original_shutil_which # Restore original shutil.which

    print("\n--- Test with potentially problematic TeX for fallback ---")
    # latex2markdown-py might not handle mismatched $ gracefully, let's see
    problematic_tex = r"This is $a complex equation with another $ sign, and a final one $ here."
    # problematic_tex = r"This has sections \section{Hello} and text." # Test basic command
    shutil.which = mock_shutil_which_pandoc_absent # Simulate Pandoc not found
    md_problem_fallback = convert_tex_to_markdown(problematic_tex)
    if md_problem_fallback:
        print("\nProblematic TeX Fallback Output:\n----------------\n", md_problem_fallback, "\n----------------")
    else:
        print("Problematic TeX fallback conversion failed.")
    shutil.which = original_shutil_which

    print("\n--- Test with empty TeX content ---")
    # Test how both Pandoc and fallback handle empty string
    print("  Testing Pandoc with empty string:")
    md_empty_pandoc = convert_tex_to_markdown("") # Pandoc path
    if md_empty_pandoc is not None:
        print("  Pandoc Empty TeX Output:", repr(md_empty_pandoc))
    else:
        print("  Pandoc Empty TeX conversion failed.")

    print("  Testing Fallback with empty string:")
    shutil.which = mock_shutil_which_pandoc_absent # Fallback path
    md_empty_fallback = convert_tex_to_markdown("")
    if md_empty_fallback is not None:
        print("  Fallback Empty TeX Output:", repr(md_empty_fallback))
    else:
        print("  Fallback Empty TeX conversion failed.")
    shutil.which = original_shutil_which


    # Test case where Pandoc fails (e.g. invalid LaTeX), expecting fallback
    invalid_tex = r"\documentclass{article} \invalidcommand"
    print("\n=== Scenario 3: Pandoc is available but fails (invalid LaTeX) ===")
    # Ensure Pandoc is "available" for this sub-test by mocking its path
    def mock_shutil_which_pandoc_present_but_will_fail(cmd):
        if cmd == "pandoc":
            return "/usr/bin/pandoc" # Simulate pandoc present (path doesn't have to be real for this mock)
        return original_shutil_which(cmd)

    shutil.which = mock_shutil_which_pandoc_present_but_will_fail

    # Temporarily mock subprocess.run to simulate Pandoc failure for this specific test case
    original_subprocess_run = subprocess.run
    def mock_subprocess_run_pandoc_fail(*args, **kwargs):
        if args[0][0] == "/usr/bin/pandoc": # or just "pandoc" if that's what's used
            raise subprocess.CalledProcessError(1, args[0], stderr="Simulated Pandoc error")
        return original_subprocess_run(*args, **kwargs)

    subprocess.run = mock_subprocess_run_pandoc_fail

    md_pandoc_fail_fallback = convert_tex_to_markdown(invalid_tex)
    if md_pandoc_fail_fallback:
         print("\nFallback Output after Pandoc failure:\n----------------\n", md_pandoc_fail_fallback, "\n----------------")
    else:
        print("Fallback also failed after Pandoc failure or Pandoc error not handled as expected.")

    subprocess.run = original_subprocess_run # Restore
    shutil.which = original_shutil_which # Restore

    print("\nConverter tests finished.")
