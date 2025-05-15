import os
import subprocess
import json

from dotenv import load_dotenv
from google import genai


load_dotenv()


def get_api_key():
    """
    Loads the Google API key from the environment variable.

    Returns:
        str: The API key.

    Raises:
        ValueError: If the GOOGLE_API_KEY environment variable is not found.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "No GOOGLE_API_KEY environment variable found. Please set it in your .env file."
        )
    return api_key


def check_upgradable_packages():
    """
    Checks for upgradable packages using the 'checkupdates' command.

    Returns:
        list: A list of upgradable package names.
    """
    try:
        result = subprocess.run(
            ["checkupdates"], capture_output=True, text=True, check=True
        )
        upgradable_packages = result.stdout.splitlines()
        return upgradable_packages
    except subprocess.CalledProcessError as e:
        print(f"Error checking for updates: {e}")
        return []


def search_for_bugs(package_name, api_key):
    """
    Searches for known bugs or issues that could break the upgrade of a given package.

    Args:
        package_name (str): The name of the package to search for.
        api_key (str): The Google API key.

    Returns:
        str: A summary of any potential problems and their solutions.
    """
    client = genai.Client(api_key=api_key)
    model = client.models

    prompt = f"""Search for any known bugs or issues that could break the upgrade of the Arch Linux package '{package_name}'.
Return a JSON object with keys 'safe' (boolean) and 'reason' (string).
'safe' should be true if there are no known issues, and false otherwise.
'reason' should be a brief explanation of why it is safe or unsafe."""

    try:
        response = model.generate_content(
            model="gemini-2.0-flash-001",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
            },
        )
        return response.text
    except Exception as e:
        return json.dumps({"safe": False, "reason": f"Error during search: {e}"})


def is_safe_to_upgrade(search_results: str) -> dict:
    """
    Determines if it's safe to upgrade a package based on the search results.

    Args:
        search_results (str): The search results from the bug search.

    Returns:
        dict: A dictionary containing the 'safe' status and 'reason'.
    """
    try:
        data = json.loads(search_results)
        return {"safe": data["safe"], "reason": data["reason"]}
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing JSON: {e}")
        return {"safe": False, "reason": f"Error parsing JSON: {e}"}


def main():
    """
    Main function to check for upgradable packages and search for potential bugs before upgrading.
    """
    try:
        api_key = get_api_key()
        upgradable_packages = check_upgradable_packages()

        results = []
        if upgradable_packages:
            for package in upgradable_packages:
                search_results = search_for_bugs(package, api_key)
                safe_to_upgrade = is_safe_to_upgrade(search_results)
                results.append({"package": package, **safe_to_upgrade})
        else:
            results.append({"message": "No upgradable packages found."})

        print(json.dumps(results, indent=4))

    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=4))


if __name__ == "__main__":
    main()
