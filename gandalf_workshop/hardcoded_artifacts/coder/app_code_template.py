import argparse


def generate_greeting(name: str = "World") -> str:
    if not name:  # Handles empty string if argparse allows it
        name = "World"
    return f"Hello, {name}!"


def main():
    parser = argparse.ArgumentParser(description="Greeter CLI application.")
    parser.add_argument("--name", type=str, help="The name to greet.")
    args = parser.parse_args()

    if args.name:
        greeting = generate_greeting(args.name)
    else:
        greeting = generate_greeting()  # Default "World"
    print(greeting)


if __name__ == "__main__":
    main()
