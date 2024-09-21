# Clean the instructional PDFs for Combatives 2.0 and save as a dictionary

import os
import json
from logging import raiseExceptions
import pandas as pd
from pypdf import PdfReader
import pdfplumber
import re


def indentify_technique_file_names(dir:str):
    # Get all files in the gracie directory
    files = os.listdir(dir)

    # Keep just the technique pdfs
    techniques = [i for i in files if "Lesson" in i]

    # Append dir to file names
    techniques = [dir + i for i in techniques]

    return techniques


def pdf_extract(file_name):
    # Parse PDF
    with pdfplumber.open(file_name) as pdf:
        pdf_text = ""
        for page in pdf.pages:
            pdf_text += page.extract_text()

    # Correct Common typos that ruin the extraction process
    pdf_text = pdf_text.replace("Refl ex Development Drill", "Reflex Development Drill")
    pdf_text = pdf_text.replace("Stage 1.5", "Stage One Point Five")

    # Identify Technical Slices Sections
    try:
        result_slices = re.search(pattern='Technical Slices(.*)Reflex Development Drill',
                           string=pdf_text,
                           flags=re.DOTALL)
        result_slices = result_slices.group(1).strip()
    except:
        raise Exception("Failure in pdf_extract: cannot find the phrase(s) 'Technical Slices' and/or 'Reflex Development Drill")

    # Section
    try:
        result_technique_name = re.search(pattern='Technique: (.*)\nPosition',
                           string=pdf_text,
                           flags=re.DOTALL)
        result_technique_name = result_technique_name.group(1).strip()
    except:
        raise Exception("Failure in pdf_extract: cannot find the phrase(s) 'Technique' and/or 'Position'")
    return result_slices, result_technique_name


def get_next_list_value(input_list: list,
                        first_value: str):
    index = input_list.index(first_value) + 1
    if index < len(input_list):
        next_value = input_list[index]
    else:
        next_value = ''

    return next_value


def get_detail_text(detail_name = 'Indicator',
                    list_of_all_details = ['Indicator', 'Essential Detail'],
                    full_string = ''
                    ):
    if detail_name in list_of_all_details:
        # Get Next Section Title
        nt = get_next_list_value(list_of_all_details, detail_name)
        if nt:
            out = re.search(pattern=f'{detail_name}: (.*){nt}',
                            string=full_string,
                            flags=re.DOTALL).group(1).strip()
        else:
            out = re.search(pattern=f'{detail_name}: (.*)',
                            string=full_string,
                            flags=re.DOTALL).group(1).strip()
    else:
        out = ''

    return out


def split_technique_string(result_slices:str):
    # Split technique string on bulleted list (formatted as: 1. Hook Sweep)
    split_techniques = re.split(pattern = r'(\d+)\.', string=result_slices)

    # Drop the list items that are integers and empty values
    split_techniques = [i for i in split_techniques  if i and not re.fullmatch(r'\d+', i)]

    # Remove the bullet points from the string
    split_techniques = [i.replace('•', '') for i in split_techniques]

    # Remove line breaks
    split_techniques = [i.replace('\n', ' ') for i in split_techniques]

    # Remove double spaces
    split_techniques = [i.replace('  ', ' ') for i in split_techniques]

    return split_techniques


def format_technique_str(result_slices:str,
                         result_technique_name:str):

    possible_details = ['Indicator', 'Essential Detail', 'Most Common Mistake', 'Most Common Mistakes',
                        'Bad Guy Reminder', 'Safety Tip',
                        'Core Principles', 'Drill Orders']

    split_techniques = split_technique_string(result_slices)

    # Format each move into the correct dictionary
    technique_dict = {}
    try:
        for i in range(0,len(split_techniques)):
            # print(f"Iteration: {i}")
            temp_string = split_techniques[i]

            # Check to see which sections this move has
            contained_values = [item for item in possible_details if item in temp_string]

            # Remove duplicate spelling
            if ('Most Common Mistake' in contained_values) & ('Most Common Mistakes' in contained_values):
                contained_values.remove('Most Common Mistake')

            contained_values = sorted(contained_values,
                                      key=lambda item: temp_string.find(item) if item in temp_string else float('inf'))

            move_name = (result_technique_name + ": " +
                         re.search(pattern=f'(.*){contained_values[0]}: ',
                                   string=temp_string,
                                   flags=re.DOTALL).group(1).strip())

            indicator = get_detail_text(detail_name = 'Indicator',
                                        list_of_all_details=contained_values,
                                        full_string=temp_string)

            essential_detail = get_detail_text(detail_name = 'Essential Detail',
                                               list_of_all_details=contained_values,
                                               full_string=temp_string)

            if 'Most Common Mistakes' in contained_values:
                mistake= get_detail_text(detail_name = 'Most Common Mistakes',
                                         list_of_all_details=contained_values,
                                         full_string=temp_string)
            else:
                mistake= get_detail_text(detail_name = 'Most Common Mistake',
                                         list_of_all_details=contained_values,
                                         full_string=temp_string)

            bad_guy_reminder= get_detail_text(detail_name = 'Bad Guy Reminder',
                                              list_of_all_details=contained_values,
                                              full_string=temp_string)

            safety_tip = get_detail_text(detail_name = 'Safety Tip',
                                         list_of_all_details=contained_values,
                                         full_string=temp_string)

            core_principles = get_detail_text(detail_name = 'Core Principles',
                                              list_of_all_details=contained_values,
                                              full_string=temp_string)

            drill_orders = get_detail_text(detail_name = 'Drill Orders',
                                           list_of_all_details=contained_values,
                                           full_string=temp_string)

            technique_dict[move_name] = {
                "Indicator": indicator,
                "Esstential Detail": essential_detail,
                "Most Common Mistake": mistake,
                "Bad Guy Reminder": bad_guy_reminder,
                "Safety Tip": safety_tip,
                "Core Principles": core_principles,
                "Drill Orders": drill_orders
            }
    except:
        print(f"Failure in format_technique_str() somewhere in the for loop")

    return technique_dict

def save_data_as_dict(dictionary, file_path):
    # Ensure the file path ends with .json. If not append or raise error
    if file_path[-5:] == ".json":
        json.dump(dictionary, open(file_path, 'w'))
    else:
        # raise Exception("file_path must end as .txt")
        raise Exception("file_path must end as .json")


def merge_dicts(existing_dict, new_dict):
    for key, value in new_dict.items():
        if key in existing_dict:
            existing_dict[key].update(value)
        else:
            existing_dict[key] = value


if __name__ == "__main__":
    dir = "../data/pdfs/gracie_combatives_2.0/"
    technique_file_paths = indentify_technique_file_names(dir)

    technique_dict = {}
    for i in technique_file_paths:
        print(i)
        result_slices, result_technique_name = pdf_extract(i)
        out_dict = format_technique_str(result_slices=result_slices,
                                              result_technique_name=result_technique_name)
        merge_dicts(technique_dict, out_dict)

    # TODO update final dict to replace "Stage One Point Five" with "Stage 1.5"
    # TODO update save process to save all files and not just the last one
    save_data_as_dict(dictionary=technique_dict,
                      file_path="../data/cleaned_data/instructionals_combatives_2.0.json")

    # print(f"\n\nThe Recorded Moves Are: {list(technique_dict.keys())}\n\n")
    #
    # for keys in list(technique_dict.keys()):
    #     example_dict = technique_dict[keys]
    #     print(f"\nThe details for {keys} are")
    #     for i in example_dict.keys():
    #         print(f"\t{i}: {example_dict[i]}")


    # List of files with bad pdf parsing:
    # "/Lesson 18_ Headlock Escape 1.pdf"
    # "Lesson 3_ Positional Control (Mount).pdf"
    # "Lesson 31_ Take the Back (Guard).pdf"
    # "Lesson 16_ Headlock Counters.pdf"
    # "Lesson 9_ Armbar (Mount).pdf"
    # "Lesson 13_ Positional Control (Side Mount).pdf"
    # "Lesson 2_ Americana Armlock.pdf"
    # "Lesson 12_ Elbow Escape (Mount).pdf"
    # "Lesson 17_ Double Leg Takedown.pdf"
    # "Lesson 8_ Punch Block Series (Stages 1-4).pdf"
    # "Lesson 24_ Shrimp Escape.pdf"
    # "Lesson 22_ Headlock Escape 2.pdf"