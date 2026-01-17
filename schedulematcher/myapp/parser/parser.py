"""
PDF Parser for Omnivox Schedule
"""

from pypdf import PdfReader
import re

DAY_MAP = {
    "Mon": "Monday",
    "Tue": "Tuesday",
    "Wed": "Wednesday",
    "Thu": "Thursday",
    "Fri": "Friday"
}

class ScheduleItem:
    def __init__(self, name, code, teacher, start_time, end_time, classroom):
        self.name = name
        self.code = code
        self.teacher = teacher
        self.startTime = start_time
        self.endTime = end_time
        self.classroom = classroom
    
    def __repr__(self):
        return f"ScheduleItem({self.name}, {self.code}, {self.teacher}, {self.startTime}, {self.endTime}, {self.classroom})"

class OmnivoxScheduleParser:
    def __init__(self, path):
        self.Path = path
        self.Reader = PdfReader(path)

    def extractScheduleText(self):
        MainPage = self.Reader.pages[0]
        scheduleText = MainPage.extract_text()
        return scheduleText

    def parseCourses(self):
        """
        Parse the PDF and return course data organized by day.
        
        Returns:
            {
                "Monday": [
                    ScheduleItem()
                ],
                "Tuesday": [...],
                ...
            }
        """
        scheduleText = self.extractScheduleText()
        lines = scheduleText.split("\n")
        
        schedule = {
            "Monday": [],
            "Tuesday": [],
            "Wednesday": [],
            "Thursday": [],
            "Friday": []
        }
        
        # Thank you claude for this tuff regex
        coursePattern = re.compile(r'^(\d+)\s{2}(.+)$')
        codePattern = re.compile(r'^(.+?)\s+sec\.(\d+),\s*teacher:\s*(.+)$')
        timePattern = re.compile(r'^(Mon|Tue|Wed|Thu|Fri)\s+(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2}),\s*classroom\s+(.+)$')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if this is a course header line
            courseMatch = coursePattern.match(line)
            if not courseMatch:
                i += 1
                continue

            courseName = courseMatch.group(2).strip()
            i += 1

            if i > len(lines):
                break

            codeLine = lines[i].strip()
            codeMatch = codePattern.match(codeLine)
            
            if not codeMatch:
                continue
            
            courseCode = codeMatch.group(1).strip()
            teacher = codeMatch.group(3).strip()

            i += 1
            while i < len(lines):
                timeLine = lines[i].strip()
                timeMatch = timePattern.match(timeLine)
                
                if not timeMatch:
                    break
                
                dayAbbrev = timeMatch.group(1)
                startTime = timeMatch.group(2)
                endTime = timeMatch.group(3)
                classroom = timeMatch.group(4).strip()
                    
                dayFull = DAY_MAP.get(dayAbbrev, dayAbbrev)
                
                schedule[dayFull].append(ScheduleItem(courseName, courseCode, teacher, startTime, endTime, classroom))

                i += 1
    
        for day in schedule:
            schedule[day].sort(key=lambda x: x.startTime)
        
        return schedule

if __name__ == "__main__":
    parser = OmnivoxScheduleParser("Omnivox.pdf")
    schedule = parser.parseCourses()

    print(schedule)