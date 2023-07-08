import json
import numpy as np
import pandas as pd
import re
from pathlib import Path
from gpa_calculator.exemption_default import default_exemption_list

EXEMPTION_FILE = Path(__file__).parent.parent / Path('exemption.json')


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
    file_path = input('Please enter the path of your transcript: ')
    quotes_marks = ['\'', '"']
    if file_path[0] in quotes_marks and file_path[-1] in quotes_marks:
        file_path = file_path[1:-1]
    return file_path


def _validate_file(file_path):
    """
    Validate whether the file is the readable Excel file, or a CSV file.

    Parameters
    ----------
    file_path: str
        The file path user specified.

    Returns
    -------
    bool
        Whether the file is the readable Excel file or not.
    """
    try:
        if file_path.endswith('.csv'):
            _ = pd.read_csv(file_path, encoding='ISO-8859-1')
        else:
            _ = pd.read_excel(file_path)
        return True
    except FileNotFoundError:
        print(f'Error: No such file or directory \'{file_path}\'')
        return False
    except ValueError:
        print('You are opening an unreadable Excel or CSV file. Please make it readable before opening. '
              'Please read the README for details.')
        return False


def open_transcript_file():
    """
    Open and validate a transcript Excel file (or CSV file).

    Returns
    -------
    DataFrame
        The content of the transcript file (in Pandas DataFrame format)
    """
    is_validated = False
    while not is_validated:
        # Input file path
        file_path = _input_file_path()
        # Validate the file
        is_validated = _validate_file(file_path)
    # Return the content of the file
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path, encoding='ISO-8859-1')
    else:
        return pd.read_excel(file_path)


def choose_mode():
    """
    Ask users to choose the mode for calculation (overall, or just 1 semester).

    Returns
    -------
    str
        The mode user has chosen
    """
    print('There are 2 modes available:\n1 - Overall\n2 - One semester')
    mode = input('Please choose mode by typing mode name or just a number (1/2): ')
    mode_dict = {
        '1': 'overall',
        '2': 'one semester'
    }
    if mode == '1' or mode == '2':
        mode = mode_dict[mode]
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
    return ''.join(formatted_name_ls)


def select_semester():
    """
    Ask users to select the semester name (if users chose "one semester" mode).

    Returns
    -------
    str
        The semester name user has chosen
    """
    semester_name = input('Please enter semester you want to select: ')
    semester_name = _format_semester_name(semester_name)
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
    """
    try:
        with open(filename, 'r') as loader:
            raw_exemption = json.load(loader)
            exemption_list = raw_exemption['exemption_subjects']
    except FileNotFoundError:
        exemption_list = default_exemption_list
    return exemption_list


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
    exemption_subjects = _load_exemption_subjects()
    modes = {
        'add': _add_exemption_subject,
        'remove': _remove_exemption_subject
    }
    while True:
        _display_exemption_subjects(exemption_subjects)
        mode = input('Please type \'add\' for adding a subject, or '
                     '\'remove\' for removing a subject, or \'ok\' to proceed: ')
        if mode == 'ok':
            break
        else:
            subject = input(f'Please specify a subject code to {mode}: '
                            f'(Just first 3 letters of the code) ').strip()
            subject = subject[:3].upper()
            exemption_subjects = modes[mode](subject, exemption_subjects)
    _save_exemption_subjects(exemption_subjects)
    return exemption_subjects


def calculating_gpa(transcript_data, mode, exemption_list, semester_name=None):
    """
    Calculate the GPA score (this is the heart of the GPA calculator).

    Parameters
    ----------
    transcript_data: DataFrame
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
    # Remove exemption subjects from the transcript data
    for subject in exemption_list:
        indexes = transcript_data[transcript_data['Subject Code'].str.find(subject) > -1].index
        transcript_data.drop(indexes, axis=0, inplace=True)
    # Retrieve only subset of transcript of a specified semester when "one semester" mode is applied
    if mode == "one semester" and semester_name:
        transcript_data = transcript_data[transcript_data['Semester'] == semester_name]
    elif mode == "one semester" and semester_name is None:
        print('You chose \'one semester\' mode but did not specify semester name.')
        return None
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
