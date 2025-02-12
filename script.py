import re
import json
import argparse

def extract_cisco_data(log_file):
    """ Extracts Cisco health check details from the given log file. """

    # Initialize a dictionary for extracted data
    cisco_data = {
        "Type": None,
        "Model": None,
        "Hostname": None,
        "IP Address": None,
        "STATUS": None,
        "IOS Version": None,
        "Suggested IOS Version": None,
        "Image Location & Name": None,
        "Flash Memory": None,
        "System Serial No.": None,
        "Uptime": None,
        "CPU STATUS": None,
        "MODULES and Hardware": None,
        "Device Hardware": None
    }

    try:
        # Read the log file
        with open(log_file, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Parse each line for key information
        for line in lines:
            # Extract hostname
            if re.match(r"^[A-Za-z0-9_-]+#", line.strip()):
                cisco_data["Hostname"] = line.strip().split("#")[0]

            # Extract IOS Version
            ios_match = re.search(r"Version\s([\d]+\.[\d]+\.[\d]+)", line)
            if ios_match:
                cisco_data["IOS Version"] = ios_match.group(1)

            # Extract Model (e.g., Catalyst 4500 L3 Switch)
            model_match = re.search(r"?:License|Licenses\s*Information\s(*[:\-]?\s*(.*?)(?:\n|$)", line)
            if model_match:
                cisco_data["Model"] = model_match.group(1)
                cisco_data["Type"] = "Switch" if "Catalyst" in model_match.group(1) else "Router"

            # Extract Serial Number
            serial_match = re.search(r"System Serial Number\s*:\s*([\w\d]+)", line, re.IGNORECASE)
            if serial_match:
                cisco_data["System Serial No."] = serial_match.group(1)

            # Extract Flash Memory
            flash_match = re.search(r"(\d+)\s*Kbytes of Flash", line)
            if flash_match:
                cisco_data["Flash Memory"] = f"{flash_match.group(1)} KB"

            # Extract Uptime
            uptime_match = re.search(r"uptime is (.*)", line, re.IGNORECASE)
            if uptime_match:
                cisco_data["Uptime"] = uptime_match.group(1)

        return cisco_data

    except Exception as e:
        print(f"Error processing file: {e}")
        return None

def save_to_json(data, output_file):
    """ Saves extracted data to a JSON file. """
    try:
        with open(output_file, "w") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"✅ Data successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving file: {e}")

if __name__ == "__main__":
    # Command-line argument parser
    parser = argparse.ArgumentParser(description="Cisco Health Check Log Parser")
    parser.add_argument("logfile", help="Path to the Cisco CLI log file")
    args = parser.parse_args()

    # Extract data and save
    extracted_data = extract_cisco_data(args.logfile)
    if extracted_data:
        output_json = "cisco_health_check.json"
        save_to_json(extracted_data, output_json)
