

def generate_handlers_report(handlers, total_requests):
    # Подготовка строк для вывода
    header = "HANDLER                \tDEBUG  \tINFO   \tWARNING\tERROR  \tCRITICAL"
    lines = [f"Total requests: {total_requests}\n", header]

    sorted_handlers = sorted(handlers.keys())
    totals = {"DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0}

    for handler in sorted_handlers:
        data = handlers[handler]
        line = (
            f"{handler:<22}\t"
            f"{data.get('DEBUG', 0):<7}\t"
            f"{data.get('INFO', 0):<7}\t"
            f"{data.get('WARNING', 0):<7}\t"
            f"{data.get('ERROR', 0):<7}\t"
            f"{data.get('CRITICAL', 0):<7}"
        )
        lines.append(line)
        for level in totals:
            totals[level] += data.get(level, 0)

    # Итоговая строка
    total_line = (
        f"{'':<22}\t"
        f"{totals['DEBUG']:<7}\t"
        f"{totals['INFO']:<7}\t"
        f"{totals['WARNING']:<7}\t"
        f"{totals['ERROR']:<7}\t"
        f"{totals['CRITICAL']:<7}"
    )
    lines.append(total_line)

    # Дублируем заголовок и итоговую строку в конце
    lines.append(header)
    lines.append(total_line)

    # Вывод в консоль
    for line in lines:
        print(line)

    return lines  # Возвращаем список строк для дальнейшего использования

def save_to_file(lines, output_file="report.txt"):
    """Сохраняет список строк в текстовый файл."""
    with open(output_file, "w") as f:
        for line in lines:
            print(line, file=f)

def generate_report(report_name, handlers, total_requests):
    if report_name == "handlers":
        return generate_handlers_report(handlers, total_requests)
    else:
        raise ValueError(f"Unknown report: {report_name}")