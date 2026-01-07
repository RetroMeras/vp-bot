from typing import Iterable
from typing import Any
import io
import csv
from typing import Self
from telegram import File

class CSVWriter:
    def __init__(self, fieldnames: list[str]):
        self.output = io.StringIO()
        self.writer = csv.DictWriter(self.output, fieldnames=fieldnames)
        self.writer.writeheader()

    def write_row(self, row: dict[str, Any]) -> Self:
        self.writer.writerow(row)
        return self

    def write_rows(self, rows: Iterable[dict[str, Any]]) -> Self:
        for row in rows:
            self.write_row(row)
        return self

    def collect(self) -> "CSVHandler":
        return CSVHandler(self.output.getvalue())


class CSVHandler:
    def __init__(self, csv: str):
        self.content = csv

    @staticmethod
    async def from_file(file: File) -> Self:
        file_bytes = await file.download_as_bytearray()
        content = file_bytes.decode("utf-8")

        return CSVHandler(content)

    @staticmethod
    def new(fieldnames: list[str]) -> CSVWriter:
        return CSVWriter(fieldnames)

    def to_file(self) -> io.BytesIO:
        return io.BytesIO(self.content.encode("utf-8"))

    def reader(self) -> csv.DictReader[str]:
        reader = csv.DictReader(io.StringIO(self.content))

        return reader