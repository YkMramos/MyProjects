import re
from collections import defaultdict

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
ERROR_PATTERN = re.compile(r"Server Error: (/[^ ]+) \[.*\] - .*")
INFO_PATTERN = re.compile(r"([^ ]+ [^ ]+ \[.*\])")

def parse_logs(log_files):
    handlers = defaultdict(lambda: defaultdict(int))
    total_requests = 0

    for log_file in log_files:
        with open(log_file, "r") as f:
            for line in f:
                error_match = ERROR_PATTERN.search(line)
                if error_match:
                    path = error_match.group(1)
                    handlers[path]["ERROR"] += 1
                    total_requests += 1
                else:
                    info_match = INFO_PATTERN.search(line)
                    if info_match:
                        path = info_match.group(1).split()[0]  # Берем только путь
                        handlers[path]["INFO"] += 1
                        total_requests += 1

    return dict(handlers), total_requests