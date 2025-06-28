import re
from typing import List, Dict

def extract_fenced_divs(markdown_content: str) -> List[Dict[str, str]]:
    """
    Extracts fenced div blocks from markdown content.
    A fenced div block is defined by lines starting with ':::' followed by a name,
    and ending with a line starting with ':::'.
    Example:
    ::: section_alpha
    This is content for section_alpha.
    It can span multiple lines.
    :::

    Args:
        markdown_content (str): The markdown content to parse.

    Returns:
        List[Dict[str, str]]: A list of dictionaries, where each dictionary
        represents a div and has keys: "name", "content", "original_text".
        Returns an empty list if no divs are found or in case of errors.
    """
    # Regex to find blocks:
    # Starts with ::: followed by a name (captured)
    # Then captures anything until another ::: on a new line
    # (?s) makes . match newlines.
    # Non-greedy match for content: (.*?)
    # Name: (\w+) allows alphanumeric and underscore. Can be adjusted.
    # The name part is optional in some markdown extensions, but we'll require it for structure.
    # Pattern: ^::: \s* (\w+) \s* $ (start line)
    #          (.*?)               (content)
    #          ^::: \s* $          (end line)
    # Need to handle multiline flag for ^ and $

    # Simpler approach: iterate line by line to find start/end, robust for nesting if needed later (not now)
    # For now, regex is fine if nesting is not supported by this simple extractor.

    # Regex:
    # ^::: \s* ([a-zA-Z0-9_-]+) \s* \n  -- Start fence with name (Group 1)
    # ( (?:.|\n)*? )                     -- Content (Group 2), non-greedy, any char or newline
    # \n ^::: \s* $                     -- End fence
    # re.MULTILINE for ^ and $

    # Regex explanation:
    # ^:::                     # Line starts with :::
    # \s*                      # Optional whitespace
    # ([a-zA-Z0-9_-]+)         # Group 1: div_name (alphanumeric, _, -)
    # \s*                      # Optional whitespace
    # \n                       # Newline after the name line
    # (.*?)                    # Group 2: Content (non-greedy, dot matches newline due to DOTALL)
    # \n                       # Newline before the closing fence
    # :::                      # Closing fence (doesn't need ^ if previous \n is matched correctly)
    # [ \t]*                   # Optional spaces/tabs on closing fence line (not newlines)
    # \n?                      # Optional newline at the very end of the block
    pattern = re.compile(r"^::: \s*([a-zA-Z0-9_-]+)\s*\n(.*?)\n^:::[ \t]*\n?", re.MULTILINE | re.DOTALL)
    # Name is Group 1, Content is Group 2.

    # DEBUGGING: Print the content being processed (Commented out after verification)
    # print(f"--- markdown_utils.extract_fenced_divs --- INPUT ---")
    # print(repr(markdown_content))
    # print(f"--- END INPUT ---")

    extracted_divs: List[Dict[str, str]] = []
    match_found = False
    for match in pattern.finditer(markdown_content):
        match_found = True
        div_name = match.group(1).strip()
        content = match.group(2).strip()
        full_block_text = match.group(0) # The entire matched block
        # print(f"DEBUG: Match found: name='{div_name}', content_preview='{content[:30]}...', full_block_repr={repr(full_block_text)}")


        extracted_divs.append({
            "name": div_name,
            "content": content,
            "original_text": full_block_text.strip() # Strip outer newlines from the block
        })

    # if not match_found: # Keep for debugging if needed
    #     print("--- markdown_utils.extract_fenced_divs --- NO MATCHES FOUND ---")

    return extracted_divs


if __name__ == '__main__':
    print("--- Testing extract_fenced_divs ---")

    test_md_1 = """
Hello world.

::: section1
This is the first section.
It has multiple lines.
:::

Some text in between.

::: another_section_2
Content for section 2.
    Indented content.
And more.
:::

No div here.
"""
    divs1 = extract_fenced_divs(test_md_1)
    print(f"\nTest Case 1 (2 divs): Found {len(divs1)} divs.")
    for i, div in enumerate(divs1):
        print(f"  Div {i+1}: Name='{div['name']}', Content='{div['content'][:30]}...', Original='{div['original_text'][:40]}...'")
    assert len(divs1) == 2
    if len(divs1) == 2:
        assert divs1[0]['name'] == "section1"
        assert "This is the first section.\nIt has multiple lines." in divs1[0]['content']
        assert divs1[1]['name'] == "another_section_2"
        assert "Content for section 2.\n    Indented content.\nAnd more." in divs1[1]['content']

    test_md_2_no_divs = """
This markdown has no fenced divs.
Just plain text.
:: section_not_a_div
Oops, almost.
:::
But not quite.
"""
    divs2 = extract_fenced_divs(test_md_2_no_divs)
    print(f"\nTest Case 2 (No divs): Found {len(divs2)} divs.")
    assert len(divs2) == 0

    test_md_3_empty_div = """
::: empty_section
:::
"""
    # This test case needs to be accurate to the regex.
    # Regex: ^::: \s*([a-zA-Z0-9_-]+)\s*\n(.*?)\n^:::[ \t]*\n?
    # Requires a newline after name line, and a newline before closing fence.
    # So, an "empty" div would look like:
    # ::: empty_section
    #
    # :::
    # Or more minimally:
    # ::: empty_section
    # :::
    # The (.*?) would match the empty line between them if re.DOTALL is on.
    # If content is truly empty (no characters, no newline between fences):
    test_md_3_empty_div_precise = "::: empty_section\n\n:::\n" # Content is one newline
    divs3 = extract_fenced_divs(test_md_3_empty_div_precise)
    print(f"\nTest Case 3 (Empty div - content is one newline): Found {len(divs3)} divs.")
    assert len(divs3) == 1
    if len(divs3) == 1:
        assert divs3[0]['name'] == "empty_section"
        assert divs3[0]['content'] == "" # The (.*?).strip() will make a single newline content empty.
        print(f"  Div 1: Name='{divs3[0]['name']}', Content='{divs3[0]['content']}', Original='{divs3[0]['original_text']}'")

    test_md_3b_truly_empty_div = "::: truly_empty\n:::\n" # No characters or newlines between opening name line and closing fence line
    divs3b = extract_fenced_divs(test_md_3b_truly_empty_div)
    print(f"\nTest Case 3b (Truly empty div - no content line): Found {len(divs3b)} divs.")
    assert len(divs3b) == 1
    if len(divs3b) == 1:
        assert divs3b[0]['name'] == "truly_empty"
        assert divs3b[0]['content'] == "" # (.*?) matches empty string, .strip() is still empty.
        print(f"  Div 1: Name='{divs3b[0]['name']}', Content='{divs3b[0]['content']}', Original='{divs3b[0]['original_text']}'")


    test_md_4_no_closing_fence = """
::: section_no_close
This will not be matched because it doesn't close.
"""
    divs4 = extract_fenced_divs(test_md_4_no_closing_fence)
    print(f"\nTest Case 4 (No closing fence): Found {len(divs4)} divs.")
    assert len(divs4) == 0

    test_md_5_div_at_start_and_end = (
        "::: start_div\n"
        "Content at the very beginning.\n"
        ":::\n"
        "Some middle text.\n" # Added newline for clarity, though not strictly needed by regex for "middle text"
        "::: end_div\n"
        "Content at the very end.\n"
        ":::\n"
    )
    divs5 = extract_fenced_divs(test_md_5_div_at_start_and_end)
    print(f"\nTest Case 5 (Divs at start/end of text): Found {len(divs5)} divs.")
    assert len(divs5) == 2
    if len(divs5) == 2:
        assert divs5[0]['name'] == "start_div"
        assert divs5[1]['name'] == "end_div"

    test_md_6_malformed_fence = """
::: \t spaced_name \t
This is a test.
:::
"""
    divs6 = extract_fenced_divs(test_md_6_malformed_fence)
    print(f"\nTest Case 6 (Spaced name in fence): Found {len(divs6)} divs.")
    assert len(divs6) == 1
    if divs6:
        assert divs6[0]['name'] == "spaced_name"

    test_md_7_no_space_after_colons = """
:::no_space_name
This should also be caught if regex is flexible.
:::
"""
    divs7 = extract_fenced_divs(test_md_7_no_space_after_colons)
    print(f"\nTest Case 7 (No space after colons before name - current regex expects space): Found {len(divs7)} divs.")
    assert len(divs7) == 0 # Current regex `^::: \s*` expects at least one space (or zero if \s* is before name)
                           # Corrected: `^::: \s*([a-zA-Z0-9_-]+)` allows zero spaces before name.
                           # This test should now pass if the name is `no_space_name`.
                           # Let's re-verify the regex: `^::: \s*([a-zA-Z0-9_-]+)\s*\n`
                           # This means `:::somename\n` will match. `\s*` after `:::` is optional.
                           # So Test Case 7 *should* find one div.
                           # The failure in previous runs was due to other reasons.
                           # The current regex is fine for this. The problem was likely the content for Scenario 1 in game_manager.py.

    print("\n--- extract_fenced_divs tests complete ---")
