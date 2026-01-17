from myapp.schedule.parser import OmnivoxScheduleParser
from myapp.models import Block, Day,Schedule,Team,User
from datetime import datetime, timedelta
import math

# Utility functions

def timeToInt(time):
    hour = int(time.split(":")[0])
    minute = int(time.split(":")[1])
    
    return hour*60 + minute

def intToTime(time):
    hour = math.floor(time/60)
    minutes = time % 60
    return str(hour).zfill(2) + ":" + str(minutes).zfill(2)


# Schedule Stuff
def generateVisualSchedule(schedule):
    events = []
    weekday_map = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4} 
    start_date = datetime(2026, 1, 5)

    for week in range(4):
        for day_index, day_blocks in enumerate(schedule):
            for block in day_blocks:
                # Get block date
                block_date = start_date + timedelta(days=weekday_map[day_index] + week*7)

                # Convert integer times to "HH:MM" string
                start_str = intToTime(block.startTime)
                end_str = intToTime(block.endTime)

                # Combine with block date to make ISO datetime
                start_dt = datetime.fromisoformat(f"{block_date.date()}T{start_str}")
                end_dt = datetime.fromisoformat(f"{block_date.date()}T{end_str}")

                events.append({
                    'title': block.name,
                    'start': start_dt.isoformat(),
                    'end': end_dt.isoformat(),
                    'color': '#007EA7'
                })


    for i in range(len(schedule)):
        for j in range (len(schedule[i])):
            block = schedule[i][j]
            print(i)
            print(block.name)
            print(block.startTime)
            print(block.endTime)
    
    return events


def pdfToSchedule(pdf):
    parse = OmnivoxScheduleParser(pdf)
    parsed_data = parse.parseCourses()

    monday_day = Day.objects.create(name="Monday")
    tuesday_day = Day.objects.create(name="Tuesday")
    wednesday_day = Day.objects.create(name="Wednesday")
    thursday_day = Day.objects.create(name="Thursday")
    friday_day = Day.objects.create(name="Friday")
    saturday_day = Day.objects.create(name="Saturday")
    sunday_day = Day.objects.create(name="Sunday")

    # Create blocks for each day
    monday_blocks = []
    for course in parsed_data["Monday"]:
        block = Block.objects.create(
            name=course.name,
            startTime=timeToInt(course.startTime),
            endTime=timeToInt(course.endTime),
            mandatory=True,
            day=monday_day
        )
        monday_blocks.append(block)

    tuesday_blocks = []
    for course in parsed_data["Tuesday"]:
        block = Block.objects.create(
            name=course.name,
            startTime=timeToInt(course.startTime),
            endTime=timeToInt(course.endTime),
            mandatory=True,
            day=tuesday_day
        )
        tuesday_blocks.append(block)

    wednesday_blocks = []
    for course in parsed_data["Wednesday"]:
        block = Block.objects.create(
            name=course.name,
            startTime=timeToInt(course.startTime),
            endTime=timeToInt(course.endTime),
            mandatory=True,
            day=wednesday_day
        )
        wednesday_blocks.append(block)

    thursday_blocks = []
    for course in parsed_data["Thursday"]:
        block = Block.objects.create(
            name=course.name,
            startTime=timeToInt(course.startTime),
            endTime=timeToInt(course.endTime),
            mandatory=True,
            day=thursday_day
        )
        thursday_blocks.append(block)

    friday_blocks = []
    for course in parsed_data["Friday"]:
        block = Block.objects.create(
            name=course.name,
            startTime=timeToInt(course.startTime),
            endTime=timeToInt(course.endTime),
            mandatory=True,
            day=friday_day
        )
        friday_blocks.append(block)

    schedule_obj = Schedule.objects.create(
        monday=monday_day,
        tuesday=tuesday_day,
        wednesday=wednesday_day,
        thursday=thursday_day,
        friday=friday_day,
        saturday=saturday_day,
        sunday=sunday_day
    )

    block_lists = [monday_blocks, tuesday_blocks, wednesday_blocks, thursday_blocks, friday_blocks]
    
    return (schedule_obj, block_lists)

#im sorry for the unholy number of loops
#it's fine it won't grow nearly to the size needed to become slow
def findVacantPlage(schedules, blockSize, earliest=480, latest=1200):
    blocks=[[],[],[],[],[],[],[]]
    for schedule in schedules:
        days=[schedule.monday,schedule.tuesday,schedule.wednesday,schedule.thursday,schedule.friday,schedule.saturday,schedule.sunday]
        for i in range(len(days)):
            for block in days[i].block_set.all():
                blocks[i].append((block.startTime,block.endTime))
    plage=[[],[],[],[],[],[],[]]
    candidates=[[],[],[],[],[],[],[]]

    for i in range(earliest,latest,15):
        for k in range(7):
            toRemove=[]
            for pair in candidates[k]:
                if pair[0]==pair[1]:
                    toRemove.append(pair)
            for pair in toRemove:
                plage[k].append((pair[0]-blockSize,pair[1]))
                candidates[k].remove(pair)
            for l in range(len(candidates[k])):
                candidates[k][l][0]+=15
            toRemove=[]
            for candidate in candidates[k]:
                for block in blocks[k]:
                    if block[0]<candidate[0]<block[1]:
                        toRemove.append(candidate)
                        break
            for item in toRemove:
                candidates[k].remove(item)
            clear=True
            for block in blocks[k]:
                if block[0]<i<block[1]:
                    clear=False
                    break
            if clear:
                candidates[k].append([i,i+blockSize])
    return plage
            
