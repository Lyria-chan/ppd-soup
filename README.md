# PPD Soup

A set of tools for downloading charts and target scores from PPD.

## Requirements

- Python 3.10 or later: [Download here](https://www.python.org/downloads/)
- Browser Support: Chrome and Edge

## Installation

1. Install Python.
2. Clone this repository or download the ZIP file:
   - Click the green "Code" button, then select "Download ZIP".
3. Unpack the ZIP file.
4. Navigate to the `setup` folder and run the following files in order:
   - `get-pip.py` to install `pip`.
   - `import-and-update-libraries.py` to install required libraries.

## Usage

- **PPD GUI Downloader**: The main downloader tool. It can download any chart available on the PPD website.
- **PPD Target Score Downloader**: Downloads target scores with multiple modes available.
- **PPD Target Score Enumerator**: Enumerates target scores based on rank and updates existing scores.

## Known Bugs

- **Niconico Download Unavailable**: Niconico downloads are currently not supported due to technical difficulties.
- **Refresh Required for New Charts**: After loading new charts, a refresh may be necessary to display them.
- **Path Not Saving Automatically**: Paths might not save immediately. If needed, manually refresh or edit the path in `assets/path.txt`.
