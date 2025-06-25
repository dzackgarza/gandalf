import argparse
import os
import shutil

def main():
    parser = argparse.ArgumentParser(description="Gandalf Trust Framework CLI")
    parser.add_argument("--prompt", type=str, required=True, help="Prompt for the AI agent")
    parser.add_argument("--unique_id", type=str, required=True, help="Unique ID for the task, used for output directory naming")

    args = parser.parse_args()

    prompt = args.prompt
    unique_id = args.unique_id

    output_dir_base = "outputs"
    output_dir_specific = os.path.join(output_dir_base, unique_id)

    # Ensure the base 'outputs' directory exists
    if not os.path.exists(output_dir_base):
        os.makedirs(output_dir_base)
        print(f"Created base output directory: {output_dir_base}")

    # Clear the specific output directory if it exists, then recreate it
    if os.path.exists(output_dir_specific):
        print(f"Output directory {output_dir_specific} already exists. Clearing its contents.")
        try:
            shutil.rmtree(output_dir_specific)
        except OSError as e:
            print(f"Error removing directory {output_dir_specific}: {e}")
            # If removal fails, try to proceed but it might cause issues
            # depending on the cause of the error.

    try:
        os.makedirs(output_dir_specific)
        print(f"Ensured output directory exists: {output_dir_specific}")
    except OSError as e:
        print(f"Error creating directory {output_dir_specific}: {e}")
        # If creation fails after attempting to clear, then exit or raise
        raise  # Re-raise the exception as this is critical

    print(f"Simulating code generation for prompt: '{prompt}'")
    print(f"Output will be in: {output_dir_specific}")

    # Placeholder for actual code generation logic
    # For now, create a dummy file to indicate activity
    dummy_file_path = os.path.join(output_dir_specific, "generated_code.txt")
    with open(dummy_file_path, "w") as f:
        f.write(f"This is placeholder code for prompt: {prompt}\n")
        f.write(f"Unique ID: {unique_id}\n")
    print(f"Created dummy file: {dummy_file_path}")

if __name__ == "__main__":
    main()
