import os
import sys
import logging
import asyncio
import time
import asyncpraw.exceptions
from openpyxl.utils.exceptions import InvalidFileException
from openpyxl import Workbook, load_workbook
from dotenv import load_dotenv
import asyncpraw
from rate_limiter import APIRateLimiter


load_dotenv(dotenv_path=".env")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

rate_limit = APIRateLimiter(logger,max_retries=3, initial_delay=5.0)

class RedditAPIClient:
    def __init__(self, read_file_path, write_file_path):
        self.reddit = asyncpraw.Reddit(
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
            user_agent=os.getenv("USER_AGENT"),
        )
        self.xlsxclient = ExcelHandler(read_file_path, write_file_path)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.reddit.close()

    @rate_limit.rate_limit
    async def get_submission_comments(self, submission_url: str, traffic: str):
        try:
            submission = await self.reddit.submission(url=submission_url)
        except asyncpraw.exceptions.InvalidURL:
            logger.warning(
                f"Invalid submission URL: {submission_url}. Skipping...")
            return
        if submission.locked or submission.archived:
            return
        comments_count = len(submission.comments)
        await self._write_comments_to_excel(submission_url, comments_count, traffic)
        logger.info(
            f"Successfully processed submission: {submission_url} with {comments_count} comments")

    async def _write_comments_to_excel(self, submission_url: str, comments_count: int, traffic: str):
        if comments_count == 0:
            await self.xlsxclient.write_data_to_sheet([submission_url, 0, traffic], "No comments")
        elif 1 <= comments_count <= 3:
            await self.xlsxclient.write_data_to_sheet([submission_url, comments_count, traffic], "3 or less comments")

    async def run(self, skip_header: bool = True):
        data = await self.xlsxclient.read_data()
        if data is None:
            logger.warning("No data to process in file!")
            return

        tasks = []
        for sheet_name, sheet_data in data.items():
            for index, row in enumerate(sheet_data):
                if skip_header and index == 0:
                    continue
                url, traffic = row
                tasks.append(self.get_submission_comments(url, traffic))
                logger.info(f"Queued: row {index} in sheet {sheet_name}")

        await asyncio.gather(*tasks)
        await self.xlsxclient.sort_output_by_traffic()
        logger.info("Processing complete!")


class ExcelHandler:
    def __init__(self, read_file_path: str, write_file_path: str):
        self.read_file_path = read_file_path
        self.write_file_path = write_file_path
        self.read_workbook = None
        self.write_workbook = Workbook()

    async def read_data(self):
        try:
            self.read_workbook = load_workbook(self.read_file_path)
            return await self._extract_data_from_workbook()
        except FileNotFoundError:
            logger.error(f"Error: File '{self.read_file_path}' not found.")
        except InvalidFileException:
            logger.error(
                "Error: Invalid file format. Please provide an Excel file.")
        except Exception as e:
            logger.error(f"Error reading file: {e}")

    async def _extract_data_from_workbook(self):
        data = {}
        for sheet_name in self.read_workbook.sheetnames:
            sheet = self.read_workbook[sheet_name]
            data[sheet_name] = [
                [cell.value for cell in row] for row in sheet.iter_rows()
            ]
        return data

    async def write_data_to_sheet(self, row_data: list, sheet_name):
        sheet = await self._get_or_create_sheet(sheet_name)
        sheet.append(row_data)
        await self._save_workbook()

    async def _save_workbook(self):
        self.write_workbook.save(self.write_file_path)

    async def _get_or_create_sheet(self, sheet_name):
        if sheet_name in self.write_workbook.sheetnames:
            return self.write_workbook[sheet_name]
        else:
            sheet = self.write_workbook.create_sheet(sheet_name)
            sheet.append(["URL", "Number of comments", "Traffic"])
            return sheet

    async def sort_output_by_traffic(self):
        for sheet_name in self.write_workbook.sheetnames:
            sheet = self.write_workbook[sheet_name]
            sorted_data = await self._sort_sheet_data_by_traffic(sheet)
            await self._replace_sheet_data(sheet, sorted_data)
        await self._save_workbook()

    async def _sort_sheet_data_by_traffic(self, sheet):
        return sorted(sheet.iter_rows(min_row=2, values_only=True), key=lambda x: x[2], reverse=True)

    async def _replace_sheet_data(self, sheet, sorted_data):
        sheet.delete_rows(2, sheet.max_row)
        for row in sorted_data:
            sheet.append(row)


async def main():
    start_time = time.time()
    try:
        async with RedditAPIClient(read_file_path=input_read_file_path,
                                   write_file_path=output_file_path) as reddit_script:
            await reddit_script.run()
    finally:
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Total execution time: {execution_time:.2f} seconds")

if __name__ == "__main__":
    input_read_file_path = sys.argv[1]
    output_file_path = sys.argv[2]

    asyncio.run(main())
