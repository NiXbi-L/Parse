import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor


def run_dynamic_parser(line):
    # Разделяем строку на аргументы
    args = line.strip().split()

    python_executable = r"C:\Users\DiXer\source\repos\Project1\Parse\.venv\Scripts\python.exe"

    # Запускаем Dynamic_parser.py с аргументами
    process = subprocess.Popen([python_executable] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Ожидаем завершения процесса и получаем вывод
    stdout, stderr = process.communicate()

    # Выводим результат
    if process.returncode == 0:
        print(f"Success: {stdout.decode()}")
    else:
        print(f"Error: {stderr.decode()}")


def main(file_path):
    # Открываем файл и читаем строки
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Используем ThreadPoolExecutor для параллельного выполнения
    with ThreadPoolExecutor() as executor:
        executor.map(run_dynamic_parser, lines)


input_file = sys.argv[1]
main(input_file)
