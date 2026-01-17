"""
PDF Parser for Omnivox Schedule
"""

from pypdf import PdfReader
from json import dumps

class OmnivoxScheduleParser:
    def __init__(self, path):
        self.Path = path
        self.Reader = PdfReader(path)

    def ExtractScheduleText(self):
        MainPage = self.Reader.pages[0]
        ScheduleText = MainPage.extract_text()

        return ScheduleText

    def FormatClass(self, Class):
        if Class.strip() == "":
            return None
        
        return Class.strip()

    def ExtractSchedule(self):
        ScheduleText = self.ExtractScheduleText().split("\n")
        IsInSchedule = False

        # Time: { mon, tue, wed, thu, fri }
        Schedule = {}

        for Line in ScheduleText:
            InsensitiveLine = Line.lower()

            IsScheduleHeader = (
                "mon" in InsensitiveLine and 
                "tue" in InsensitiveLine and
                "wed" in InsensitiveLine and
                "thu" in InsensitiveLine and
                "fri" in InsensitiveLine
            )

            IsScheduleFooter = (
                "generated" in InsensitiveLine
            )

            if IsScheduleHeader:
                IsInSchedule = True
                continue

            if IsScheduleFooter:
                IsInSchedule = False
                break

            if IsInSchedule:
                Data = Line.split(" ")
                
                Schedule[Data[0]] = {
                    "mon": self.FormatClass(Data[1]),
                    "tue": self.FormatClass(Data[2]),
                    "wed": self.FormatClass(Data[3]),
                    "thu": self.FormatClass(Data[4]),
                    "fri": self.FormatClass(Data[5]),
                }
        
        return Schedule
    
    def ExtractCourses(self):
        ScheduleText = self.ExtractScheduleText().split("\n")
        
        # Data
        Courses = {}
        
        # Context Variables
        IsInCourses = False

        JmpCount = 3
        

        for Line in ScheduleText:
            # Skip irrelevant lines
            if IsInCourses and JmpCount > 0:
                JmpCount -= 1
                continue


            InsensitiveLine = Line.lower()

            IsCourse = (
                "to access omnivox" in InsensitiveLine
            )

            if IsCourse:
                IsInCourses = True
                continue

            # Extract courses
            if IsInCourses:
                Line
        
        return Courses

if __name__ == "__main__":
    ScheduleParser = OmnivoxScheduleParser("Omnivox.pdf")
    print(dumps(ScheduleParser.ExtractSchedule(), indent=4))
    print(dumps(ScheduleParser.ExtractCourses(), indent=4))