# cython: language_level=3
import csv
cimport cython
from cpython.list cimport PyList_Append

@cython.boundscheck(False)
@cython.wraparound(False)
def data_parse(str file_path) -> list:
    """
    Читает CSV и возвращает список dict с полями:
    name, email, address, date_of_birth, phone_number, job, company
    """

    cdef list people = []
    cdef object reader
    cdef object row
    cdef str name, email, addr_part1, addr_part2, state, dob, phone, job, company
    cdef int i
    cdef list comps = []

    with open(file_path, "r", encoding="utf-8", newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            all_empty = True
            for i in range(len(row)):
                if row[i] and row[i].strip():
                    all_empty = False
                    break
            if all_empty:
                continue

            if len(row) < 9:
                row = list(row) + [''] * (9 - len(row))
            name = row[0].strip()
            email = row[1].strip()
            addr_part1 = row[2].strip()
            addr_part2 = row[3].strip()
            state = row[4].strip()
            dob = row[5].strip()
            phone = row[6].strip()
            job = row[7].strip()
            if len(row) <= 8:
                company = ""
            else:
                
                for i in range(8, len(row)):
                    comps.append(row[i].strip())
                company = ", ".join([c for c in comps if c != ""])

            if addr_part1 and addr_part2:
                address = f"{addr_part1} {addr_part2}, {state}" if state else f"{addr_part1} {addr_part2}"
            elif addr_part1:
                address = f"{addr_part1}, {state}" if state else addr_part1
            else:
                address = f"{addr_part2}, {state}" if addr_part2 and state else (state or "")

            PyList_Append(people, {
                "name": name,
                "email": email,
                "address": address,
                "date_of_birth": dob,
                "phone_number": phone,
                "job": job,
                "company": company
            })

    return people
