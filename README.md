# GPA Calculator v2

This software is a console-based tool used to calculate the GPA score for
FPT University students using their transcript Excel file downloaded from
FAP (FPT University Academic Portal) website.

## 1. How to get the tool:

It is very simple, as the zip file contains pre-compiled and installed
exe file of the tool. Just go to the
[**Release**](https://github.com/NTHieu2k1/gpa-calculator-v2/releases)
section (the latest version), and download the zip file (**not** the
source code zip file). After that, you just need to extract the zip file,
go to the folder where you have just extracted the file, and click on the
.exe file in it. And then, you are good to go.

## 2. How to re-format the transcript Excel file:
After downloading a transcript Excel file from FAP website, it is **CRUCIAL**
to re-format the file before putting into the tool, because the original
file cannot be properly read (due to incorrect format) and may lead to errors
in calculation.

To re-format the original transcript file, please following the steps:

- **Step 1**: Open the file in Excel. When you see the notification below,
click "Yes".

![](/images/preprocess_step_1.png)

- **Step 2**: Click *Save* or press Ctrl+S. When a notification occurs like
below, click "No". A *Save As* window will appear, just save a new file.

![](/images/preprocess_step_2.png)

**Note**: The tool only supports 3 main Excel formats:
* **XLSX**
* **XLS**
* **CSV**

## 3. How to calculate the GPA score:
When you open the tool, please follow the instructions below to calculate
your GPA score:

- **Step 1**: Specify the path of your reformatted file (if you have not
done yet, please follow the [Section 2](#2-how-to-pre-process-the-transcript-excel-file)
above).
- **Step 2**: You can choose either *Overall* or *One semester* mode for
calculation. If you choose *One semester* mode, make sure that you specify
the semester name (for example, Fall 2022, Fall2022 or FA22).
- **Step 3**: Review the exemption subjects. These subjects would not be
used in the calculation process. You can add or remove subjects to the
list (if do so, just specify the first 3 letters of the subject code).

Now the tool will calculate the GPA score for you, based on your selection,
and display the final score.

## 4. How to run from source:

### a. Prerequisites:
First of all, a Python environment is required, so please **install Python
first** (Python 3 is recommended). Next, as there are several dependencies
for the tool, it is recommended to run the tool in a **virtual environment**.
You can refer how to create a virtual environment
[here](https://www.geeksforgeeks.org/creating-python-virtual-environment-windows-linux/).

### b. Step 1: Clone this repo:
You can use this command to clone this repo to your machine:

`git clone https://github.com/NTHieu2k1/gpa-calculator-v2.git`

### c. Step 2: Switch the current directory to the repo's directory:
You can use this command:

`cd gpa-calculator-v2`

### d. Step 3: Install dependencies:
This is the **MOST IMPORTANT** step, as the tool cannot run properly
without those dependencies installed. If you have created a virtual environment,
just activate the environment before installing. After that, as the dependencies
are defined in `requirements.txt` file, you can just use this command to
install required dependencies:

`pip install -r requirements.txt`

### e. Step 4: Run the tool:
To run the tool, just type this command:

`python run.py`