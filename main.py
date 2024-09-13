from fastapi import FastAPI, Request, Response
from fastapi.templating import Jinja2Templates
from repositories import ScriptRepository, SettingRepository
from schemas import Script, ScriptOut, Config, Setting
from datetime import datetime, timezone

'''
1 2 3 4 5 6 7 8
hig
med
low
lig
cus_1 (base 100)
cus_2 (base 200)
spec_1
spec_2

[cus_1 hz (4)][cus_2 hz (4)] | [noise hz (4)][index (4)]
[delay|loop] | [padding]
[0000] [0000] | [delay] [loop] [0000] [0000] | [delay] [loop]
[0000] [0000] | [delay] [loop] [0000] [0000] | [delay] [loop]
[0000] [0000] | [delay] [loop] [0000] [0000] | [delay] [loop]
[0000] [0000] | [delay] [loop] [0000] [0000] | [delay] [loop]
[0000] [0000] | [delay] [loop] [0000] [0000] | [delay] [loop]
[0000] [0000] | [delay] [loop] [0000] [0000] | [delay] [loop]
[0000] [0000] | [delay] [loop] [0000] [0000] | [delay] [loop]
[0000] [0000] | [delay] [loop] [0000] [0000] | [delay] [loop]

4bytes
2bytes * sc
20bytes

unit 5

head
[begin_time]
[cus_1 hz] [cus_2 hz] [noise hz]

scripts
script
[tone (tone type | noise)] [echo (tone type | noise)] [delay] [loop]


get
begin_time <-> now => index delay loop -> head

[head (4)]
[scripts (16)] (bytes)

1. minutes = now - begin
2. big_loop = minutes / sum(time_of_phrases)
    - big_loop = 0: delta_big_loop = minutes
    - big_loop > 0: delta_big_loop = minutes - big_loop * sum(time_of_phrases)
3. for phrase in phrases:
    - if delta_big_loop > sum(<-time_of_phrase): countinue;
    - else: in_phrase = phrase; break; ....
4.  unit_time_of_phrase
'''

app = FastAPI()
templates = Jinja2Templates(directory='templates')
db_path = 'alert.db'

@app.get('/')
async def get_scripts(request: Request):
    scriptRepository = ScriptRepository(db_path)
    settingRepository = SettingRepository(db_path)
    return templates.TemplateResponse('board.html', {
        'request': request,
        'scripts': scriptRepository.get_scripts(),
        'setting': settingRepository.get_setting('script'),
    })

@app.get('/new')
async def new_script(request: Request):
    tone_options = [(0, 'Off'), (1, 'High'), (2, 'Medium'), (3, 'Low'), (4, 'Custom 1'), (5, 'Custom 2'), (6, 'Special 1'), (7, 'Special 2')]
    yes_no_options = [(0, 'No'), (1, 'Yes')]
    delay_options = [(i, f'{i * 5} mins' if i < 12 else f'{i - 12} hour' if i == 12 else f'{i - 12} hour {((i - 12) * 5)} mins') for i in range(16)]
    loop_options = [(i, str(i)) for i in range(32)]

    script = ScriptOut(
        id=0,
        name='',
        begin=datetime.now(timezone.utc),
        config=Config(custom_1=0, custom_2=0, noise=0),
        phrases=[],
        phrases_bytes=None
    )

    return templates.TemplateResponse('script.html', {
        'is_create': True,
        'request': request,
        'script': script,
        'tone_options': tone_options,
        'yes_no_options': yes_no_options,
        'delay_options': delay_options,
        'loop_options': loop_options,
    })

def pharses_to_bytes(phrases):
    phrases_bytes = bytes([])
    for p in phrases:
        phrases_bytes = phrases_bytes + bytes([p.tone << 5 | p.tone_noise << 4 | p.echo << 1 | p.echo_noise, p.delay << 4 | p.loop])
    
    return phrases_bytes

@app.post('/new')
async def new_script_submit(script: Script):
    scriptRepository = ScriptRepository(db_path)
    script.phrases_bytes = pharses_to_bytes(script.phrases)
    scriptRepository.insert_script(script)
    return {'status': 'success', 'message': 'Data created successfully'}

@app.get('/update/{id}')
async def update_script(request: Request, id: int):
    tone_options = [(0, 'Off'), (1, 'High'), (2, 'Medium'), (3, 'Low'), (4, 'Custom 1'), (5, 'Custom 2'), (6, 'Special 1'), (7, 'Special 2')]
    yes_no_options = [(0, 'No'), (1, 'Yes')]
    delay_options = [(i, f'{i * 5} mins' if i < 12 else f'{i - 12} hour' if i == 12 else f'{i - 12} hour {((i - 12) * 5)} mins') for i in range(16)]
    loop_options = [(i, str(i)) for i in range(32)]

    scriptRepository = ScriptRepository(db_path)
    script = scriptRepository.get_script(id)

    return templates.TemplateResponse('script.html', {
        'request': request,
        'is_create': False,
        'script': script,
        'tone_options': tone_options,
        'yes_no_options': yes_no_options,
        'delay_options': delay_options,
        'loop_options': loop_options,
    })

@app.put('/update/{id}')
async def update_script_submit(id: int, script: Script):
    scriptRepository = ScriptRepository(db_path)
    script.phrases_bytes = pharses_to_bytes(script.phrases)
    print(pharses_to_bytes(script.phrases))
    scriptRepository.update_script(id, script)
    return {'status': 'success', 'message': 'Data updated successfully'}

@app.delete('/delete/{id}')
async def update_script_submit(id: int):
    scriptRepository = ScriptRepository(db_path)
    scriptRepository.delete_script(id)
    return {'status': 'success', 'message': 'Data deleted successfully'}

@app.put('/settings/script')
async def update_script_submit(setting: Setting):
    settingRepository = SettingRepository(db_path)
    return settingRepository.update_script('script', setting.value)

def cal_requirements_of_header_seg(begin, phrases):
    if len(phrases) == 0:
        return (0, 0, 0)

    timediff = int((datetime.now() - begin).total_seconds() / 60)
    ph = [p.dict() for p in phrases]
    sum_time_of_cycle = 0

    for p in ph:
        p['unit_time'] = 5 + p['delay'] * 5
        p['sum_time'] = (5 + p['delay'] * 5) * (1 + p['loop'])
        sum_time_of_cycle += p['sum_time']
    
    cycle_times = timediff // sum_time_of_cycle

    print(timediff, cycle_times, sum_time_of_cycle, begin, datetime.now())
    # 23 2 10 2024-09-13 10:02:00 2024-09-13 10:25:07.616816
    # 23 2 10 2024-09-13 10:02:00 2024-09-13 10:25:07.616816

    if cycle_times != 0:
        timediff = timediff - cycle_times * sum_time_of_cycle

    print(timediff, cycle_times, sum_time_of_cycle, begin, datetime.now())
    # 5 2 10 2024-09-13 10:02:00 2024-09-13 10:27:06.454330
    
    in_phrase = ph[0]
    index = 0
    for p in ph:
        if p['sum_time'] >= timediff:
            timediff = timediff - p['sum_time']
            continue
        else:
            index += 1
            in_phrase = p
    else:
        in_phrase = ph[0]
        index = 0
    
    loop = timediff // in_phrase['unit_time']
    if loop != 0:
        timediff = timediff - loop * in_phrase['unit_time']
    
    delay = (timediff - 5) // 5

    return (index, delay, loop)

@app.get('/get')
async def update_script_submit():
    settingRepository = SettingRepository(db_path)
    scriptRepository = ScriptRepository(db_path)
    sid = settingRepository.get_setting('script').value
    config_bytes = bytes([0, 0, 0, 0])
    pharses_bytes = bytes([0, 0, 0, 0])

    try:
        script = scriptRepository.get_script(int(sid))
        roh = cal_requirements_of_header_seg(script.begin, script.phrases)
        config_bytes = bytes([
            (script.config.custom_1 << 4 | script.config.custom_2) & 0xFF,
            (script.config.noise << 4 | roh[0]) & 0xFF,
            (roh[1] << 4 | roh[2]) & 0xFF,
            0
        ])
        pharses_bytes = script.phrases_bytes
    except:
        print("heheheheheeheheheheeheheheeheh")
        config_bytes = bytes([0, 0, 0, 0])
        pharses_bytes = bytes([0, 0, 0, 0])

    return Response(content=config_bytes + pharses_bytes, media_type="application/octet-stream")
