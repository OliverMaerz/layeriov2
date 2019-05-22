from typing import List


class MasterSheet:
    """Class to hold the sheet data and manage the shares."""

    available_sheets = []

    def __init__(self, available_sheets: List[str]):
        self.available_sheets = available_sheets

    @classmethod
    def from_dummy_data(cls):
        """Initialize MasterSheet with dummy data."""
        available_sheets = ["HRReport", "Actuals", "Assumptions", "Dashboard"]
        return cls(available_sheets)

    @classmethod
    def empty(cls):
        """Initialize MasterSheet with empty sheet."""
        available_sheets = []
        return cls(available_sheets)

    @classmethod
    def from_excel(cls):
        """Initialize MasterSheet with data from Excel file."""
        pass

    @classmethod
    def from_csv(cls):
        """Initialize MasterSheet with data from CSV file."""
        pass

    @classmethod
    def from_google_sheet(cls):
        """Initialize MasterSheet with data from Google Sheets."""
        pass

    def check_sheet(self, sheet_name: str):
        """Returns True if sheet_name is valid, False otherwise.

        Keyword arguments:
        sheet_name -- str with name of sheet
        """

        if sheet_name in self.available_sheets:
            return True
        else:
            return False
