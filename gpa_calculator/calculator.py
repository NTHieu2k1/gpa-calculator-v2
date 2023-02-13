from gpa_calculator.art import logo
from gpa_calculator.utils import (open_transcript_file, choose_mode, select_semester,
                                  check_exemption_subjects, calculating_gpa, display_gpa_score)


def main():
    """
    This function contains the main process of the whole calculator.
    """
    print(logo)

    # Open & validate student transcript Excel file
    transcript = open_transcript_file()

    while True:
        # Choose mode (overall/1 semester)
        mode = choose_mode()
        if mode == 'one semester':
            semester_name = select_semester()
        else:
            semester_name = None

        # Ask whether users wants to edit list of exemption subjects
        exemption_subjects = check_exemption_subjects()

        # Calculate GPA score & display the score
        gpa_score = calculating_gpa(transcript, mode, exemption_subjects, semester_name=semester_name)
        display_gpa_score(gpa_score)

        # Calculate again, or exit
        cont = input('Do you want to calculate again? (Y/N) ')
        if cont[0].upper() == 'N':
            break
        print()
