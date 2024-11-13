# WinnerOdds Bookmaker Analyzer

Curious about your performance across different bookmakers but unsure how to organize or extract data from your personal WinnerOdds .csv file? Then this open-source, user-friendly .csv analyzer _(with a GUI)_ is perfect for you!

To use it, download the .csv file from your [WinnerOdds](https://www.winnerodds.com/#lay64) history page, run the program, select the .csv file, and wait a few seconds for the .html file to be generated. You'll then have your detailed report ready.

Currently working with tennis data only, but I am planing to add support for both soccer and table tennis in the future. You can downloaded the compiled .exe file [here](https://github.com/lines64/WinnerOdds-Analyzer/releases).

## Screenshots

![App Screenshot](https://github.com/lines64/WinnerOdds-Analyzer/blob/main/Screenshots/WinnerOdds%20Tennis%20Bookmakers%20Analysis.png)

![App Screenshot](https://github.com/lines64/WinnerOdds-Analyzer/blob/main/Screenshots/WinnerOdds%20Tennis%20Bookmakers%20Analysis%20(2b).png)

![App Screenshot](https://github.com/lines64/WinnerOdds-Analyzer/blob/main/Screenshots/WinnerOdds%20Tennis%20Bookmakers%20Analysis%20(3).png)

## How to Run / Install

The executable (.exe) file for the betting_analysis.pyw script is already available under the [Releases section](https://github.com/lines64/WinnerOdds-Analyzer/releases) of this repository. You can download and run it directly on a Windows system without needing Python installed.

## Creating an Executable (.exe) from the Python Script

If you prefer to generate your own `.exe` file, you can follow the instructions below.

### Prerequisites

- **Python Installation**: Ensure you have Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

- **Install PyInstaller**: PyInstaller is the tool we will use to create the executable. You can install it via pip:

  ```bash
  pip install pyinstaller

### Steps to Create the Executable

1. **Navigate to the Script's Directory**: Open your command prompt or terminal and navigate to the directory where `betting_analysis.pyw` is located. For example:

   ```bash
   cd path/to/your/script

2. **Run PyInstaller**: Use PyInstaller to create the executable. The basic command is:

   ```bash
   pyinstaller --onefile betting_analysis.pyw

4. **Run the Executable**: Navigate to the dist folder, where you can now run the `.exe` file directly on a Windows system without requiring Python to be installed.

### TODO
    - Add soccer support
    - Add table tennis support

## Feedback

If you have any feedback, please reach out to me at info@lines64.com. Contributions are always welcome!
