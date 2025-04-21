from cli import parse_args
from log_parser import parse_logs
from report_generator import generate_report, save_to_file

def main():
    args = parse_args()
    handlers, total_requests = parse_logs(args.log_files)
    report_lines = generate_report(args.report, handlers, total_requests)
    save_to_file(report_lines, output_file=args.output)

if __name__ == "__main__":
    main()