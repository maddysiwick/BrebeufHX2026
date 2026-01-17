from myapp.schedule.parser import OmnivoxScheduleParser

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
    schedule = parse.parseCourses()

    monday = []
    tuesday = []
    wednesday = []
    thursday = []
    friday = []

    for i in range(len(schedule["Monday"])):
        day = Day.objects.create(name="Monday")
        monday.append(Block.objects.create(name=schedule["Monday"][i].name, 
                                           startTime=timeToInt(schedule["Monday"][i].startTime), 
                                           endTime=timeToInt(schedule["Monday"][i].endTime),
                                           mandatory=True,
                                           day=day))

    for i in range(len(schedule["Tuesday"])):
        day = Day.objects.create(name="Tuesday")
        tuesday.append(Block.objects.create(name=schedule["Tuesday"][i].name, 
                                            startTime=timeToInt(schedule["Tuesday"][i].startTime), 
                                            endTime=timeToInt(schedule["Tuesday"][i].endTime),
                                            mandatory=True,
                                            day=day))
    
    for i in range(len(schedule["Wednesday"])):
        day = Day.objects.create(name="Wednesday")
        wednesday.append(Block.objects.create(name=schedule["Wednesday"][i].name, 
                                              startTime=timeToInt(schedule["Wednesday"][i].startTime), 
                                              endTime=timeToInt(schedule["Wednesday"][i].endTime),
                                              mandatory=True,
                                              day=day))
        
    for i in range(len(schedule["Thursday"])):
        day = Day.objects.create(name="Thursday")
        thursday.append(Block.objects.create(name=schedule["Thursday"][i].name, 
                                             startTime=timeToInt(schedule["Thursday"][i].startTime), 
                                             endTime=timeToInt(schedule["Thursday"][i].endTime),
                                             mandatory=True,
                                             day=day))
        
    for i in range(len(schedule["Friday"])):
        day = Day.objects.create(name="Friday")
        friday.append(Block.objects.create(name=schedule["Friday"][i].name, 
                                           startTime=timeToInt(schedule["Friday"][i].startTime), 
                                           endTime=timeToInt(schedule["Friday"][i].endTime),
                                           mandatory=True,
                                           day=day))
    
    return [monday, tuesday, wednesday, thursday, friday]

