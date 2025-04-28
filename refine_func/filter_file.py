import csv
import re


def filter_ecu_data(input_file, output_file):
    """
    Reads a log file, filters lines containing 'data.ecu',
    parses the fields, and writes them to a structured CSV.
    
    :param input_file: Path to the input log file (txt)
    :param output_file: Path to the output CSV file
    """
    filtered_entries = []

    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            if 'data.ecu' in line:
                parts = line.strip().split('\t', 4)
                if len(parts) >= 5:
                    date, time, level, source, rest = parts

                    # Try to split rest into description and value using last group of 2+ spaces
                    match = re.match(r'(.+?)\s{2,}(.+)', rest.strip())
                    if match:
                        description, value = match.groups()
                    else:
                        description, value = rest.strip(), ""

                    filtered_entries.append([date, time, level, source, description, value])

    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Time", "Level", "Source", "Description", "Value"])
        for entry in filtered_entries:
            writer.writerow(entry)


# Example usage
input_filename = "AndrOBD.log.4.txt"
output_filename = "filtered_data.txt"
filter_ecu_data(input_filename, output_filename)
