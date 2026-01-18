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
def generateVisualSchedule(schedule, color="#007EA7"):
    events = []
    weekday_map = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6} 
    start_date = datetime(2026, 1, 5)  # First Monday of calendar
    num_weeks = 52  # Generate a full year of events

    for day_index, day_blocks in enumerate(schedule):
        for block in day_blocks:
            is_recurring = getattr(block, 'isRecurring', True)
            specific_date = getattr(block, 'specificDate', None)
            
            if is_recurring:
                # Recurring event - show on every week
                for week in range(num_weeks):
                    block_date = start_date + timedelta(days=weekday_map[day_index] + week*7)
                    
                    # Convert integer times to "HH:MM" string
                    start_str = intToTime(block.startTime)
                    end_str = intToTime(block.endTime)

                    start_dt = datetime.fromisoformat(f"{block_date.date()}T{start_str}")
                    end_dt = datetime.fromisoformat(f"{block_date.date()}T{end_str}")

                    event_color = "#28a745" if "Team Meeting" in block.name else color

                    events.append({
                        'id': block.id,
                        'title': block.name,
                        'start': start_dt.isoformat(),
                        'end': end_dt.isoformat(),
                        'color': event_color,
                        'editable': True,
                        'isRecurring': True
                    })
            else:
                # One-time event - only show on its specific date
                if specific_date:
                    start_str = intToTime(block.startTime)
                    end_str = intToTime(block.endTime)
                    
                    date_str = specific_date.isoformat() if hasattr(specific_date, 'isoformat') else str(specific_date)
                    
                    start_dt = datetime.fromisoformat(f"{date_str}T{start_str}")
                    end_dt = datetime.fromisoformat(f"{date_str}T{end_str}")
                    
                    event_color = "#28a745" if "Team Meeting" in block.name else color
                    
                    events.append({
                        'id': block.id,
                        'title': block.name,
                        'start': start_dt.isoformat(),
                        'end': end_dt.isoformat(),
                        'color': event_color,
                        'editable': True,
                        'isRecurring': False
                    })
    
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

    block_lists = [monday_blocks, tuesday_blocks, wednesday_blocks, thursday_blocks, friday_blocks, [], []]
    
    return (schedule_obj, block_lists)

#im sorry for the unholy number of loops
#it's fine it won't grow nearly to the size needed to become slow
def findVacantPlage(schedules, blockSize, earliest=480, latest=1200, start_date=None):
    blocks=[[],[],[],[],[],[],[]]
    for schedule in schedules:
        days=[schedule.monday,schedule.tuesday,schedule.wednesday,schedule.thursday,schedule.friday,schedule.saturday,schedule.sunday]
        for i in range(len(days)):
            for block in days[i].block_set.all():
                if getattr(block, 'isRecurring', True):
                    blocks[i].append((block.startTime,block.endTime))
                else:
                    # One-time events only block the specific day they occur on
                    # This is a simplification for the 'generic week' view
                    # Ideally we'd only block if we're looking at that specific week
                    # For now, let's treat them as blocking for simplicity or ignore them
                    # If we ignore them, the common time found might be occupied by a one-time event
                    # Let's ignore one-time events for the GENERIC OVERLAP to avoid over-constraining
                    pass
    print(blocks)
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
    events = []
    scored_slots = [[] for _ in range(7)]
    
    # Pre-calculate scores for each slot
    for day_idx, day_slots in enumerate(plage):
        for start_minute, end_minute in day_slots:
            # Score calculation: average buffer time for all users
            total_buffer = 0
            for schedule in schedules:
                user_days = [schedule.monday, schedule.tuesday, schedule.wednesday, schedule.thursday, schedule.friday, schedule.saturday, schedule.sunday]
                day_blocks = user_days[day_idx].block_set.all()
                
                # Find closest block before and after
                before_gap = start_minute - 480 # Default start of day
                after_gap = 1200 - end_minute   # Default end of day
                
                for b in day_blocks:
                    if b.endTime <= start_minute:
                        before_gap = min(before_gap, start_minute - b.endTime)
                    if b.startTime >= end_minute:
                        after_gap = min(after_gap, b.startTime - end_minute)
                
                # We want large gaps, but diminishing returns after a certain point (e.g., 60 mins)
                # Also reward "centered" meetings (gap on both sides)
                total_buffer += min(before_gap, 60) + min(after_gap, 60)
            
            avg_score = total_buffer / len(schedules) if schedules else 0
            scored_slots[day_idx].append({
                'start': start_minute,
                'end': end_minute,
                'score': avg_score
            })

    if start_date:
        for day_idx, day_slots in enumerate(scored_slots):
            day_date = start_date + timedelta(days=day_idx)
            for slot in day_slots:
                start_minute, end_minute = slot['start'], slot['end']
                start_time = day_date + timedelta(minutes=start_minute)
                end_time = day_date + timedelta(minutes=end_minute)
                events.append({
                    "title": "Available",
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "score": slot['score']
                })
    
    for k in range(7):
        print(f"Day {k+1} scored slots: {scored_slots[k]}")
        
    return plage, events
   
   
            
