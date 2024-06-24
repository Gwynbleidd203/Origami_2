Number = float | int

def create_report(
        content: Number | str,
        writting_path: str,
):
    """
        Create a report with all the data collected during the resising process as a '.txt' file
    """
    with open('report.txt',  'w') as report_file:

        report_file.write(content)