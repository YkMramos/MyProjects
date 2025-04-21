import argparse
import os

VALID_REPORTS = ["handlers"]

def parse_args():
    parser = argparse.ArgumentParser(description="Django log analyzer")
    parser.add_argument("log_files", nargs="+", help="Paths to log files")
    parser.add_argument("--report", required=True, choices=VALID_REPORTS, help="Report type to generate")
    parser.add_argument("--output", default="handlers_report.txt", help="Output file for the report")
    args = parser.parse_args()

    for log_file in args.log_files:
        if not os.path.exists(log_file):
            parser.error(f"Log file {log_file} does not exist")

    return args