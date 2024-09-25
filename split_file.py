import os
import sys


def split_file(the_file_name, the_chunk_size, out_folder_name="result_split_files"):
    with open(the_file_name, "r") as in_file:
        text = in_file.read()
        chunks = [text[i:i + the_chunk_size] for i in range(0, len(text), the_chunk_size)]
        os.system(f"mkdir -p {out_folder_name}")
        for i, chunk in enumerate(chunks):
            with open(f"{out_folder_name}/{i}.txt", "w") as out_file:
                out_file.write(chunk)


if __name__ == "__main__":
    arguments = sys.argv[1:]
    file_name = arguments[0]
    chunk_size = 4999
    split_file(file_name, chunk_size, "result_split_files")
