"""
PDF Parser for Omnivox Schedule
"""

from pypdf import Pdfreader
from json import dumps

class OmnivoxScheduleParser:
    def __init__(self, path):
        self.path = path
        self.reader = Pdfreader(path)

    def extractscheduleText(self):
        mainPage = self.reader.pages[0]
        scheduleText = mainPage.extract_text()

        return scheduleText

    def formatClass(self, Class):
        if Class.strip() == "":
            return None
        
        return Class.strip()

    def extractSchedule(self):
        scheduleText = self.extractscheduleText().split("\n")
        isInSchedule = False

        # Time: { mon, tue, wed, thu, fri }
        Schedule = {}

        for Line in scheduleText:
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
                isInSchedule = True
                continue

            if IsScheduleFooter:
                isInSchedule = False
                break

            if isInSchedule:
                Data = Line.split(" ")
                
                Schedule[Data[0]] = {
                    "mon": self.formatClass(Data[1]),
                    "tue": self.formatClass(Data[2]),
                    "wed": self.formatClass(Data[3]),
                    "thu": self.formatClass(Data[4]),
                    "fri": self.formatClass(Data[5]),
                }
        
        return Schedule
    
    def ExtractCourses(self):
        scheduleText = self.extractscheduleText().split("\n")
        
        # Data
        Courses = {}
        
        # Context Variables
        IsInCourses = False

        JmpCount = 3
        

        for Line in scheduleText:
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
    print(dumps(ScheduleParser.extractSchedule(), indent=4))
    print(dumps(ScheduleParser.ExtractCourses(), indent=4))