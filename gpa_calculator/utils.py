import json
import numpy as np
import pandas as pd
import re
from pathlib import Path
from gpa_calculator.exemption_default import default_exemption_list
import tkinter as tk
from tkinter import filedialog as fd

EXEMPTION_FILE = Path(__file__).parent.parent / Path('exemption.json')

COLUMNS_FORMAT = np.array(['No', 'Term', 'Semester', 'Subject Code', 'prerequisite',
                           'Replaced Subject', 'Subject Name', 'Credit', 'Grade', 'Status'])


def display_logo(logo):
    print(logo)


def _input_file_path():
    """
    Ask user to enter a file path (usually the path of user's student transcript Excel file or CSV file).

    Returns
    -------
    str
        The file path user specified.
    """
    file_path = input('Please enter the path of your transcript: ').strip()
    if file_path == '':
        return None
    quotes_marks = ['\'', '"']
    if file_path[0] in quotes_marks and file_path[-1] in quotes_marks:
        file_path = file_path[1:-1]
    return file_path


def _load_file(file_path):
    """
    Load the file with the path specified.

    Parameters
    ----------
    file_path: str
        The file path user specified.

    Returns
    -------
    pd.DataFrame
        The content of the transcript file (if validated) or None otherwise
    """
    contents = None
    try:
        if file_path.endswith('.csv'):
            try:
                contents = pd.read_csv(file_path)
            except UnicodeDecodeError:
                contents = pd.read_csv(file_path, encoding='ISO-8859-1')
        else:
            contents = pd.read_excel(file_path)
        if np.array_equal(contents.columns, COLUMNS_FORMAT):
            return contents
        else:
            print('Data format not supported. Please choose an another file.')
            return None
    except FileNotFoundError:
        print(f'Error: No such file or directory \'{file_path}\'')
        return None
    except ValueError:
        # Read the raw, downloaded transcript file
        contents = pd.read_html(file_path)[0]
        contents.columns = COLUMNS_FORMAT
        return contents
    except:
        print('Invalid input. Please input again.')
        return None


def _select_file():
    """
    Ask user to select the transcript file, in the GUI manner.

    Returns
    -------
    str
        The path of the selected file
    """
    file_types = (
        ('Microsoft Excel files', '*.xls;*.xlsx'),
        ('CSV files', '*.csv')
    )
    print('Selecting file...', end=' ')
    win = tk.Tk()
    try:
        file_path = fd.askopenfilenames(title='Open a file', initialdir='/', filetypes=file_types)[0]
        print('Done')
        print(f'Loading content from {file_path}')
        win.destroy()
        return file_path
    except IndexError:
        print('Failed')
        win.destroy()
        return None


def _unify_n_fillna(content):
    """
    Unify the content to one single-table structure (if there is a sub-table in the content,
    as well as fill missing data (on Credits and Grades).

    Parameters
    ----------
    content: pd.DataFrame
        The raw content of the transcript file

    Returns
    -------
    DataFrame
        Clean, unified transcript content
    """
    # Unify if there is a sub-table in the content (separated by a space/NaN line)
    space_idx = content[content.No.isna()].index
    size_orig = len(content)
    if len(space_idx) > 0:
        for i in range(2):
            content.drop(space_idx, axis=0, inplace=True)
            space_idx += 1
    else:
        space_idx = content[content.Status.isna()].index

    if len(space_idx) > 0:
        sub_idx = pd.RangeIndex(space_idx.values[0], size_orig, 1)
        source = ['Subject Name', 'Replaced Subject', 'prerequisite', 'Subject Code', 'Semester', 'Term']
        dest = ['Status', 'Grade', 'Credit', 'Subject Name', 'Subject Code', 'Semester']

        for i in range(len(source)):
            content.loc[sub_idx, dest[i]] = content.loc[sub_idx, source[i]]

        content.loc[sub_idx, 'Term'] = 0
        content.loc[sub_idx, 'prerequisite'] = np.nan
        content.loc[sub_idx, 'Replaced Subject'] = np.nan

    # Fill missing credits & grades
    missing_credit_idx = content[content.Credit.isna()].index
    missing_grade_idx = content[content.Grade.isna()].index
    content.loc[missing_credit_idx, 'Credit'] = 0
    content.loc[missing_grade_idx, 'Grade'] = 0
    return content


def open_transcript_file():
    """
    Open and validate a transcript Excel file (or CSV file).
    Or exit when user want to quit

    Returns
    -------
    DataFrame
        The content of the transcript file (in Pandas DataFrame format)
    """
    content = None
    is_validated = False
    while not is_validated:
        # Input file path
        file_path = _select_file()
        # No input -> input again
        if not file_path:
            print('No input detected. Please input again.')
            continue
        if file_path[:] == 'exit' or file_path[:] == 'quit':
            exit(0)
        # Validate the file
        content = _load_file(file_path)
        is_validated = content is not None
    # Return the content of the file
    return _unify_n_fillna(content)


def choose_mode():
    """
    Ask users to choose the mode for calculation (overall, or just 1 semester).

    Returns
    -------
    str
        The mode user has chosen
    """
    is_validated = False
    while not is_validated:
        print('There are 2 modes available:\n1 - Overall\n2 - One semester')
        mode = input('Please choose mode by typing mode name or just a number (1/2): ').strip()
        mode_dict = {
            '1': 'overall',
            '2': 'one semester'
        }
        if mode == '1' or mode == '2':
            mode = mode_dict[mode]
            is_validated = True
            continue
        print('Invalid input. Please input again.')
    return mode.lower()


def _format_semester_name(semester_name):
    """
    Format the semester name to the right format for calculation.

    Parameters
    ----------
    semester_name: str
        The semester name user entered

    Returns
    -------
    str
        The formatted semester name
    """
    semester_name = semester_name.strip().lower()
    semester_abbr = {
        'sp': 'Spring',
        'su': 'Summer',
        'fa': 'Fall'
    }
    formatted_name_ls = []
    for abbr in semester_abbr.keys():
        if len(re.findall(abbr, semester_name)) > 0:
            formatted_name_ls.append(semester_abbr[abbr])
            break
    numbers_ls = re.findall('[0-9]+', semester_name)
    if len(numbers_ls[-1]) == 2:
        formatted_name_ls.append('20' + numbers_ls[-1])
    elif len(numbers_ls[-1]) == 4:
        formatted_name_ls.append(numbers_ls[-1])
    if len(formatted_name_ls) != 2:
        raise ValueError('Invalid semester name')
    return ''.join(formatted_name_ls)


def select_semester():
    """
    Ask users to select the semester name (if users chose "one semester" mode).

    Returns
    -------
    str
        The semester name user has chosen
    """
    is_validated = False
    while not is_validated:
        semester_name = input('Please specify the semester name: ').strip()
        try:
            semester_name = _format_semester_name(semester_name)
            is_validated = True
        except:
            print('Invalid input. Please input again.')
    return semester_name


def _load_exemption_subjects(filename=EXEMPTION_FILE):
    """
    Load the list of exemption subjects from file.

    Parameters
    ----------
    filename: str, optional
        The path of the file used to load the exemption subjects

    Returns
    -------
    list
        The list of exemption subjects
    str
        The notification indicates load from user preferences (json file) or default
    """
    try:
        with open(filename, 'r') as loader:
            raw_exemption = json.load(loader)
            exemption_list = raw_exemption['exemption_subjects']
            notify = 'user_pref'
    except FileNotFoundError:
        exemption_list = default_exemption_list
        notify = 'default'
    return exemption_list, notify


def _display_exemption_subjects(exemption_list):
    """
    Display the list of exemption subjects.

    Parameters
    ----------
    exemption_list: list
        The list of exemption subjects

    Returns
    -------
    None
    """
    print('Here is the list of exemption subjects:')
    for subject in exemption_list:
        print(f'- {subject}')


def _add_exemption_subject(subject, exemption_list):
    """
    Add a subject to the exemption subjects list.

    Parameters
    ----------
    subject: str
        The subject name user wants to add
    exemption_list: list
        The list of exemption subjects

    Returns
    -------
    list
        The exemption list after adding a subject
    """
    exemption_list.append(subject)
    return exemption_list


def _remove_exemption_subject(subject, exemption_list):
    """
    Remove a subject from the exemption subjects list.

    Parameters
    ----------
    subject: str
        The subject name user wants to remove
    exemption_list: list
        The list of exemption subjects

    Returns
    -------
    list
        The exemption list after removing a subject
    """
    exemption_list.remove(subject)
    return exemption_list


def _save_exemption_subjects(exemption_list, filename=EXEMPTION_FILE):
    """
    Save the list of exemption subjects to a file.

    Parameters
    ----------
    exemption_list: list
        The list of exemption subjects
    filename: str, optional
        The path of the file used to save the exemption subjects

    Returns
    -------
    None
    """
    exemption_dict = {
        'exemption_subjects': exemption_list
    }
    with open(filename, 'w') as writer:
        json.dump(exemption_dict, writer)


def check_exemption_subjects():
    """
    Ask user to check the exemption list, as well as add or remove subjects in the exemption list if needed.

    Returns
    -------
    list
        List of exemption subjects
    """
    exemption_subjects, notify = _load_exemption_subjects()
    modes = {
        'add': _add_exemption_subject,
        'remove': _remove_exemption_subject
    }
    if notify == 'user_pref':
        print('Loaded from user preferences (exemption.json file).')
    elif notify == 'default':
        print('User preferences (exemption.json file) not found. Loaded from default list.')
    while True:
        _display_exemption_subjects(exemption_subjects)
        mode = input('Please type \'add\' for adding a subject, or '
                     '\'remove\' for removing a subject, or \'ok\' to proceed (default is \'ok\'): ').strip()
        if mode == '':
            mode = 'ok'
        if mode == 'ok':
            break
        elif mode != 'add' and mode != 'remove':
            print('Invalid input. Please input again.')
        else:
            subject = input(f'Please specify a subject code to {mode}: '
                            f'(Just first 3 letters of the code) ').strip()
            try:
                subject = subject[:3].upper()
                exemption_subjects = modes[mode](subject, exemption_subjects)
            except:
                print('Invalid input. Failed to perform the operation.')
    _save_exemption_subjects(exemption_subjects)
    print('Saved to exemption.json file.')
    return exemption_subjects


def calculating_gpa(transcript_data_orig, mode, exemption_list, semester_name=None):
    """
    Calculate the GPA score (this is the heart of the GPA calculator).

    Parameters
    ----------
    transcript_data_orig: DataFrame
        The content of the transcript
    mode: str
        The mode for calculation (overall/one semester)
    exemption_list: list
        The list of exemption subjects
    semester_name: str, optional
        The semester name (this must be specified if the mode is "one semester")

    Returns
    -------
    float
        The final GPA score
    """
    transcript_data = transcript_data_orig.copy()
    # Remove exemption subjects from the transcript data
    for subject in exemption_list:
        indexes = transcript_data[transcript_data['Subject Code'].str.find(subject) > -1].index
        transcript_data.drop(indexes, axis=0, inplace=True)
    # Retrieve only subset of transcript of a specified semester when "one semester" mode is applied
    if mode == "one semester" and semester_name:
        transcript_data.query('Semester == @semester_name', inplace=True)
    elif mode == "one semester" and semester_name is None:
        print('You chose \'one semester\' mode but did not specify semester name.')
        return None
    # Retrieve only already studied subjects for calculation
    studying = 'Studying'
    not_start = 'Not started'
    transcript_data.query('Status != @studying and Status != @not_start',
                          inplace=True)
    # Return 0 immediately when there is no subjects for calculation
    if len(transcript_data) == 0:
        return 0
    # Calculate the GPA
    total_weighted_grades = np.sum(transcript_data['Grade'].values * transcript_data['Credit'].values)
    total_credits = np.sum(transcript_data['Credit'])
    gpa_score = total_weighted_grades / total_credits
    return gpa_score


def display_gpa_score(gpa_score):
    """
    Display the final GPA score.

    Parameters
    ----------
    gpa_score: int64
        The final GPA score

    Returns
    -------
    None
    """
    print(f'Your GPA score is: {gpa_score:.2f}')


def confirm_again():
    """
    Ask user to calculate again, or exit.
    """
    is_validated = False
    while not is_validated:
        cont = input('Do you want to calculate again? (Y/N) ').strip()
        if cont != '' and (cont[0].upper() == 'Y' or cont[0].upper() == 'N'):
            is_validated = True
            continue
        print('Invalid input. Please input again')
    return cont[0].upper() == 'Y'
