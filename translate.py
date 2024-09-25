import os
import re
import sys
import glob
from googletrans import Translator
from split_file import split_file

translate_limit = 4998
source_language = "Chinese"
destination_language = "English"


def translate_text(text, should_clean: bool):
    paragraph_size = 50
    translator = Translator(service_urls=['translate.google.com'])
    if len(text) > translate_limit:
        print(f"text exceeded the {paragraph_size} character limit")
        return

    the_translation = translator.translate(text, src='zh-cn', dest='en')

    return clean_text(the_translation.text, paragraph_size) if should_clean else the_translation.text


def clean_text(text, paragraph_size):
    the_txt_sentences = text.split(".")
    the_txt_sentences = [f"{sentence}." for sentence in the_txt_sentences]
    the_chunks = ['\n'.join(the_txt_sentences[i:i + paragraph_size])
                  for i in range(0, len(the_txt_sentences), paragraph_size)]

    return '\n\n'.join(the_chunks)


def get_files_to_translate(dir_path):
    file_paths = []
    for file_path in glob.glob(os.path.join(dir_path, "*.txt")):
        pattern = r"^(.*/)?\d+[.]txt$"
        if os.path.isfile(file_path) and re.match(pattern, file_path):
            file_paths.append(file_path)

    print(f"files to be translated : {file_paths}\nfrom: {source_language} to: {destination_language}")
    return file_paths


# If a folder was given as parameter:
def translate_dir(dir_path, out_path, should_clean=False):
    tmp_directory = "tmp_dir"
    os.system(f"mkdir -p tmp_dir")
    file_paths = get_files_to_translate(dir_path)
    file_paths.sort(key=lambda x: int(re.findall(r'\d+', x)[0]))

    for file_path in file_paths:
        curr_dir = os.path.dirname(file_path)
        new_file_name = curr_dir + "_" + os.path.splitext(os.path.basename(file_path))[0] + "_translated.txt"
        translate_single_file(file_path, tmp_directory, new_file_name, should_clean)

    join_files_in_dir(tmp_directory, out_path)
    # Cleanup
    os.system(f"rm -r {tmp_directory}")


def join_files_in_dir(directory, out_dir, res_file_name="translation_result.txt"):
    with open(os.path.join(out_dir, res_file_name), "w") as out_file:
        relevant_paths = glob.glob(os.path.join(directory, "*.txt"))
        relevant_paths = [path for path in relevant_paths if os.path.isfile(path) and "translat" in path]
        relevant_paths.sort(key=lambda x: int(re.findall(r'\d+', x)[0]))
        for file_path in relevant_paths:
            if os.path.isfile(file_path) and "translat" in file_path:
                with open(file_path, "r") as curr_file:
                    curr_file_text = curr_file.read()
                    out_file.write(curr_file_text)


def translate_single_file(file_path, out_dir, res_file_name="translation_result.txt", should_clean=False):
    print(f"file to be translated : {file_path}\nfrom: {source_language} to: {destination_language}")

    with open(file_path, "r") as the_curr_file:
        the_curr_text = the_curr_file.read()
        if len(the_curr_text) > translate_limit:
            print("file is too big to translate, splitting it first")
            split_dir = "tmp_for_split"
            split_file(file_path, translate_limit, split_dir)
            translate_dir(split_dir, out_dir, should_clean)
            os.system(f"rm -r {split_dir}")

        else:
            translation = translate_text(the_curr_text, should_clean)
            with open(os.path.join(out_dir, res_file_name), "w") as out_file:
                out_file.write(translation)


def does_out_file_exist(out_file_path):
    if os.path.isfile(out_file_path):
        user_input = input(f"file {out_file_path} already Exist,"
                           f" do you ant to override it?(y for yes, otherwise cancels).\n")
        if user_input.lower() != "y":
            print("You didn't enter 'y' sos the operation waws cancelled.")
            exit(3)


if __name__ == "__main__":
    should_format = False
    if len(sys.argv) < 2:
        print("usage: python3 translate.py <file_path:str> [should_format?:bool]")
        exit(2)

    param_to_program = sys.argv[1]
    if len(sys.argv) >= 3:
        should_format = bool(sys.argv[2])

    expected_out_file = os.path.join(os.getcwd(), "translation_result.txt")
    does_out_file_exist(expected_out_file)

    if os.path.isdir(param_to_program):
        translate_dir(param_to_program, os.getcwd(), should_clean=should_format)

    elif os.path.isfile(param_to_program):
        translate_single_file(param_to_program, os.getcwd(), should_clean=should_format)
