
class course_record:
    def __init__(self, course, weight, letter, GPA_weight):
        self.GPA_weight = GPA_weight
        self.course = course
        self.letter = letter
        self.weight = weight
        if self.letter.upper() == "A+":
            self.earned = self.weight * GPA_weight*1
        elif self.letter.upper() == "A":
            self.earned = self.weight * GPA_weight*(0.9375)
        elif self.letter.upper() == "B+":
            self.earned = self.weight * GPA_weight*(0.875)
        elif self.letter.upper() == "B":
            self.earned = self.weight * GPA_weight*(0.75)
        elif self.letter.upper() == "C+":
            self.earned = self.weight * GPA_weight*(0.625)
        elif self.letter.upper() == "C":
            self.earned = self.weight * GPA_weight*(0.5)
        elif self.letter.upper() == "D+":
            self.earned = self.weight * GPA_weight*(0.375)
        elif self.letter.upper() == "D":
            self.earned = self.weight
        else:
            self.earned = 0

    def myfunc(self):
        if self.earned == 0:
            return f"Course: {self.course}, not counted, letter is: {self.letter}"
        else:
            return f"Course: {self.course}, earned hours: {self.earned} out of {self.weight*self.GPA_weight}"

def Calculate_GPA(course_records):
    Total_Earned = 0
    Quality_Hours = 0
    for i in range(len(course_records)):
        if course_records[i].earned != 0:
            Quality_Hours += course_records[i].weight
        Total_Earned += course_records[i].earned
    if Quality_Hours == 0:
        Quality_Hours = 1
    return str(Total_Earned / Quality_Hours)

def Get_records_from_file(inputfilepath, GPA_weight):
    records = []
    try:
        with open(inputfilepath, "rt") as inputfile:
            for line in inputfile:
                if(line=="\n"):
                    continue
                record_data = line.split()
                records.append(
                    course_record(
                        record_data[0].strip(),
                        float(record_data[1].strip()),
                        record_data[2].strip(),
                        GPA_weight
                    )
                )
    except:
        print('wrong in reading data')
        exit()
    return records, GPA_weight

def Put_data_in_file(course_records, outputfile):
    (course_records, GPA_weight) = course_records
    GPA = Calculate_GPA(course_records)
    try:
        with open(outputfile, "wt") as outputfile:
            for course_record in course_records:
                outputfile.write(course_record.myfunc() + "\n")
            outputfile.write("\n")
            outputfile.write(f'final_GPA: {GPA} out of {GPA_weight}')
            outputfile.write("\n")
    except:
        print("Error in writing to file")
        exit()
    return 'success in putting data in file'


# #how to use the code:
course_records = Get_records_from_file(inputfilepath="courses_records.txt", GPA_weight=4)
print(Put_data_in_file(course_records=course_records, outputfile="Final_GPA.txt"))
