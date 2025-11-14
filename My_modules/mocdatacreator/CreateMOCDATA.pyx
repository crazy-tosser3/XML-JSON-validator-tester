# cython: language_level=3
import cython
from faker import Faker
import os
import time

@cython.boundscheck(False)
@cython.wraparound(False)
def CheckFileName(str file_path) -> str:
    cdef str base, ext
    base, ext = os.path.splitext(file_path)

    if not os.path.exists(file_path):
        return file_path

    cdef int counter = 1

    while True:
        new_file_path = f"{base}_{counter}{ext}"

        if not os.path.exists(new_file_path):
            return new_file_path

        counter+=1


@cython.boundscheck(False)
@cython.wraparound(False)
def create_moc(int how_much_person, str save_path):

    cdef float time_start = time.time()
    cdef object fake = Faker()
    cdef int i
    cdef list batch = []
    cdef int BATCH_SIZE = 1000
    cdef str line
    path = os.path.join(save_path, "people.txt")
    path = CheckFileName(path)

    with open(path, "a", encoding="utf-8") as f:
        for i in range(how_much_person):
            line = f"{fake.name()}, {fake.email()}, {fake.address().replace('\n', ', ')}, {fake.date_of_birth()}, {fake.phone_number()}, {fake.job()}, {fake.company()}\n"
            batch.append(line)
            if len(batch) >= BATCH_SIZE:
                f.write("".join(batch))
                batch.clear()
        if batch:
            f.write("".join(batch))

    cdef float time_end = time.time()

    print(f"Время выполнения: {(time_end - time_start):.2f}")
