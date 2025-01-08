import praw
import os
import sys
import logging
from openpyxl.utils.exceptions import InvalidFileException
from openpyxl import Workbook, load_workbook
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RedditAPIClient:
    def __init__(self, read_file_path, write_file_path):
        self.reddit = praw.Reddit(
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
            user_agent=os.getenv("USER_AGENT"),
        )
        self.xlsxclient = ExcelHandler(read_file_path, write_file_path)

    def get_submission_comments(self, submission_url: str, trafic: str):
        submission = self.reddit.submission(url=submission_url)
        is_locked = submission.locked
        is_archived = submission.archived
        if is_locked or is_archived:
            return
        comments = submission.comments
        comments_count = len(comments)
        if comments_count == 0:
            self.xlsxclient.write_data_to_sheet(
                [submission_url, 0, trafic], "No comments")
        elif 1 <= comments_count <= 3:
            self.xlsxclient.write_data_to_sheet(
                [submission_url, comments_count, trafic], "3 or less comments")
        else:
            pass

    def run(self, skip_header: bool = True):
        data = self.xlsxclient.read_data()
        if data is None:
            return
        for sheet_name, sheet_data in data.items():
            for index, row in enumerate(sheet_data):
                url, trafic = row
                if skip_header and index == 0:
                    continue
                self.get_submission_comments(url, trafic)
                logger.info(f"Processed: row {index} in sheet {sheet_name}")
        self.xlsxclient.sort_output_by_traffic()
        logger.info("Processing complete!")


class ExcelHandler:
    def __init__(self, read_file_path, write_file_path):
        self.read_file_path = read_file_path
        self.write_file_path = write_file_path
        self.read_workbook = None
        self.write_workbook = Workbook()

    def read_data(self):
        """Reads data from the read Excel file and returns a dictionary of sheet data."""
        try:
            self.read_workbook = load_workbook(self.read_file_path)
            data = {}
            for sheet_name in self.read_workbook.sheetnames:
                sheet = self.read_workbook[sheet_name]
                data[sheet_name] = [
                    [cell.value for cell in row] for row in sheet.iter_rows()
                ]
            return data
        except FileNotFoundError:
            logger.error(f"Error: File '{self.read_file_path}' not found.")
        except InvalidFileException:
            logger.error(
                "Error: Invalid file format. Please provide an Excel file.")
        except Exception as e:
            logger.error(f"Error reading file: {e}")

    def write_data_to_sheet(self, row_data: list, sheet_name):
        if sheet_name in self.write_workbook.sheetnames:
            sheet = self.write_workbook[sheet_name]
        else:
            sheet = self.write_workbook.create_sheet(sheet_name)
            sheet.append(["URL", "Number of comments", "Traffic"])
        sheet.append(row_data)

        self.write_workbook.save(self.write_file_path)

    def sort_output_by_traffic(self):
        for sheet_name in self.write_workbook.sheetnames:
            sheet = self.write_workbook[sheet_name]
            sorted_data = sorted(sheet.iter_rows(
                min_row=2, values_only=True), key=lambda x: x[2], reverse=True)
            sheet.delete_rows(2, sheet.max_row)
            for row in sorted_data:
                sheet.append(row)
        self.write_workbook.save(self.write_file_path)


if __name__ == "__main__":
    input_read_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    reddit_script = RedditAPIClient(
        read_file_path=input_read_file_path, write_file_path=output_file_path)
    reddit_script.run()
