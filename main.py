"""
main.py - The Main Entrance to the Gandalf Workshop

This script serves as the primary command-line interface for interacting with
the Gandalf Workshop. It's like the front gate where clients arrive to submit
new commissions. Upon receiving a request (a "prompt"), this script will
initialize the WorkshopManager and instruct it to begin the process, starting
with the creation of a Blueprint.
"""

import argparse
import uuid
import os # Import os
from pathlib import Path # Import Path
from dotenv import load_dotenv # Import load_dotenv

# Construct path to .env file relative to main.py's location
# Assumes main.py is in the project root, and .env is also in the project root.
dotenv_path = Path(__file__).resolve().parent / '.env'
# print(f"Attempting to load .env from: {dotenv_path}") # Diagnostic
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path, override=True)
else:
    print(f"Warning: .env file not found at {dotenv_path}. Environment variables may not be loaded.")

# Test immediately if the key is loaded
# print(f"GEMINI_API_KEY in main.py after load_dotenv (path: {dotenv_path}): {os.getenv('GEMINI_API_KEY')}") # Diagnostic, can be removed

from gandalf_workshop.workshop_manager import WorkshopManager

# Metaphor: This is the main reception desk or commission intake point of the
# workshop. A client (user) arrives with a request (prompt), and the process
# begins here.


def main():
    """
    Main function to handle command-line arguments and initiate a new commission.
    Metaphor: The chief clerk receives a new commission request from a client,
    assigns it a unique tracking number, and forwards it to the Workshop
    Manager to commence the design phase (Blueprint creation).
    """
    # load_dotenv() # Moved to top of script
    parser = argparse.ArgumentParser(
        description=("Gandalf Workshop CLI - Submit a new commission.")
    )
    parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="The user's request or description for the new commission.",
    )
    # Potentially add more arguments later, e.g., --commission_id,
    # --config_file

    args = parser.parse_args()

    print("Gandalf Workshop: Received new commission request.")

    # Generate a unique commission ID
    # Metaphor: A unique serial number is stamped onto the new commission's
    # docket.
    commission_id = f"commission_{uuid.uuid4().hex[:8]}"
    print(f"Gandalf Workshop: Assigning Commission ID: {commission_id}")

    user_prompt = args.prompt
    print(f'Gandalf Workshop: User Prompt: "{user_prompt}"')

    # Call the Workshop Manager's method to execute the full commission workflow.
    # Metaphor: The Manager is instructed to oversee the entire commission from
    #           start to finish, including all new review stages.
    try:
        # Initialize WorkshopManager for V1.
        manager = WorkshopManager()

        # Call the V1 commission workflow.
        # This method returns the path to the product on success or raises an exception on failure.
        product_path = manager.run_v1_commission(
            user_prompt=user_prompt, commission_id=commission_id
        )

        # If run_v1_commission completes without raising an exception, it's a success.
        print(
            (
                f"Gandalf Workshop: Commission '{commission_id}' processed "
                f"successfully. Product available at: {product_path}"
            )
        )
    except ValueError as ve:
        if "GEMINI_API_KEY environment variable not set" in str(ve):
            print(
                "Error: The GEMINI_API_KEY was not found. "
                "Please ensure it is set in your .env file or environment."
            )
            # Optionally, log to a logger if configured
            # logger.error("Stopping execution: GEMINI_API_KEY not found.")
            return # Exit if API key is missing
        else:
            print( # Print other ValueErrors before full traceback
                (
                    f"Gandalf Workshop: A ValueError occurred while processing "
                    f"commission '{commission_id}': {ve}"
                )
            )
            import traceback
            traceback.print_exc()
    except Exception as e:
        print(
            (
                f"Gandalf Workshop: A critical error occurred while processing "
                f"commission '{commission_id}': {e}"
            )
        )
        # Add more sophisticated error handling or logging here
        # For example, log the stack trace
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Metaphor: The workshop doors are opened, ready for new commissions.
    main()
