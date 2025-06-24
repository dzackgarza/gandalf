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

    # Initialize the Workshop Manager
    # Metaphor: The Workshop Manager is summoned to oversee the new commission.
    manager = WorkshopManager()

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
        # Initialize WorkshopManager. Consider making max_pm_review_cycles configurable if needed.
        manager = WorkshopManager(max_pm_review_cycles=3)

        success = manager.execute_full_commission_workflow(
            user_prompt=user_prompt, commission_id=commission_id
        )

        if success:
            print(
                (
                    f"Gandalf Workshop: Commission '{commission_id}' processed "
                    "successfully."
                )
            )
        else:
            print(
                (
                    f"Gandalf Workshop: Commission '{commission_id}' failed or was "
                    "halted during processing."
                )
            )

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
