import os
import sys
import json
from datetime import datetime
from googletrans import Translator
from translate import translate_single_file


def convert_timestamp(timestamp: str) -> str:
    """
    Convert a timestamp in the format of "seconds.milliseconds" to a string in the format of "hh:mm:ss".
    Args:
        timestamp(str): A timestamp in the format of "seconds.milliseconds".

    Returns:
        str: A string in the format of "hh:mm:ss".
    """
    # Split the input timestamp into seconds and milliseconds
    if "." not in timestamp:
        timestamp += ".000"
    parts = timestamp.split('.')
    seconds = int(parts[0])
    milliseconds = int(parts[1])
    # Calculate the total time in seconds including the fraction
    total_seconds = seconds + milliseconds / 1000

    # Convert the total time to hours, minutes, and seconds
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    # Calculate the remaining milliseconds
    remaining_milliseconds = int((total_seconds - int(total_seconds)) * 1000)

    # Format the time in hh:mm:ss,SSS format
    formatted_time = f"{hours:02}:{minutes:02}:{seconds:02},{remaining_milliseconds:03}"
    return formatted_time



def extract_json(file_path: str) -> list[dict]:
    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    # Extract the desired information from the body
    body = json_data['body']
    extracted_data = [{"from": convert_timestamp(str(item['from'])), "to": convert_timestamp(str(item['to'])),
                       "content": item['content']}
                      for item in body]

    # Display the extracted data
    return extracted_data


def translate_text(text: str) -> str:
    translator = Translator()
    translated = translator.translate(text, src='zh-cn', dest='en')
    return translated.text


def new_file(data: list[dict], slow_mode, translate) -> None:
    now = datetime.now()
    counter = 1
    temp_file_name = f"{now}_tmp.txt"
    sub_file_name = f"{now}_subtitles.srt"
    if translate:
        if slow_mode:
            for i, item in enumerate(data):
                try:
                    print(f"Translating line {i}/{len(data)}...")
                    item['content'] = translate_text(item['content'])
                except Exception as e:
                    print(f"Error translating line {i}/{len(data)}: {e}")
                    item['content'] = item['content']
        else:
            sep = '\n00:00:00\n'
            text = sep.join([item['content'] for item in data])
            with open(temp_file_name, 'w') as file:
                file.write(text)

            translate_single_file(temp_file_name, os.getcwd(), should_clean=False)
            with open('translation_result.txt', 'r') as file:
                translated_txt = file.read()
                translated_txt = translated_txt.split(sep)
                for i, item in enumerate(data):
                    try:
                        item['content'] = translated_txt[i]
                    except IndexError:
                        item['content'] = translate_text(item['content'])

    with open(temp_file_name, 'w') as file:
        for item in data:
            str_to_print = f"{counter}\n{str(item['from'])} --> {item['to']}\n{str(item['content'])}\n\n"
            file.write(str_to_print)
            counter += 1

    os.system(f"mv '{temp_file_name}' '{sub_file_name}'")
    os.system(f"rm -f '{temp_file_name}'")
    os.system(f"rm -f translation_result.txt")
    print(f"subtitle file {sub_file_name} created successfully")


def create_subtitle_file(file_path: str, slow_mode: bool = False, translate: bool = False) -> None:
    # Extract the JSON data
    data: list[dict] = extract_json(file_path)
    new_file(data, slow_mode, translate)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: python3 convert_to_subtitles.py <file_path:str> <slow_mode:bool=False?> <translate:bool=False?>")
        exit(2)

    if_slow_mode = False
    if_translate = False
    if len(sys.argv) == 3:
        if_slow_mode = True if sys.argv[2].lower() == 'true' else False

    if len(sys.argv) == 4:
        if_translate = True if sys.argv[3].lower() == 'true' else False

    create_subtitle_file(sys.argv[1], if_slow_mode, if_translate)
