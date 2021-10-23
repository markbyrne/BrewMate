import os
import glob
import time
from datetime import datetime
import save_data
from gpiozero import DigitalOutputDevice

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# Reading located in base_dir + tprobe + device_file
base_dir = '/sys/bus/w1/devices/'
file = '/w1_slave'
# Temperature Probes
t_probes = {
	't1':
	{
		'DEVICE_ID':'28-0000071e097c',
		'BREW_ID': 'K20210212',
		'IDEAL_TEMP': 78.0,
		'TOLERANCE': 1.0,
		'HEATER': 'h1'
	}
}

# Heaters
heaters ={
	'h1': DigitalOutputDevice("GPIO26")
}

def read_temp_raw(t_probe):
    device_file = base_dir+t_probes[t_probe]['DEVICE_ID']+file
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp(t_probe):
    try:
        lines = read_temp_raw(t_probe)
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c
    except Exception as e:
        print(e)
        print("RETURNED 0. PLEASE LOOK INTO ERROR")
        return 0

while True:
    reports = {}
    start = time.time()

    # gather readings for a minute
    while time.time()-start<=60:
        for t_probe_id in t_probes:
            if not t_probe_id in reports.keys():
                reports[t_probe_id] = []

            temp_c = read_temp(t_probe_id)
            temp_f = temp_c * 9.0 / 5.0 + 32.0

            if  t_probes[t_probe_id]['HEATER']:
                if temp_f < t_probes[t_probe_id]['IDEAL_TEMP']-(t_probes[t_probe_id]['TOLERANCE']*0.5) and heaters[t_probes[t_probe_id]['HEATER']].value == 0:
                    print("HEATER "+t_probes[t_probe_id]['HEATER']+" TURNED ON")
                    heaters[t_probes[t_probe_id]['HEATER']].on()
                elif temp_f >= t_probes[t_probe_id]['IDEAL_TEMP']+(t_probes[t_probe_id]['TOLERANCE']*0.75) and heaters[t_probes[t_probe_id]['HEATER']].value == 1:
                    print("HEATER "+t_probes[t_probe_id]['HEATER']+" TURNED OFF")
                    heaters[t_probes[t_probe_id]['HEATER']].off()

            reports[t_probe_id].append(temp_f)
            time.sleep(1.0/len(t_probes))

    # after a minute, save results
    for t_probe_id in t_probes:
        avg_temp = sum(reports[t_probe_id])/len(reports[t_probe_id])
        print(t_probe_id+" AVERAGE TEMP (F):", avg_temp)
        try:
            heater_value = ''
            if t_probes[t_probe_id]['HEATER'] is not None:
                heater_value = heaters[t_probes[t_probe_id]['HEATER']].value
            save_data.save_temp(t_probes[t_probe_id]['BREW_ID'], datetime.now().strftime("%m/%d/%Y %H:%M:%S"), avg_temp, heater_value)
        except Exception as e:
            print(e)
            print("ERROR OCCURED WHEN SAVING DATA FOR: "+t_probe_id)
