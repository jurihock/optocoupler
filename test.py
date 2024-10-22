from etc import Logger, LxiDevice

def pwm(frequency=1, duty=0.5, level=(0, 1.5), seconds=False):

    generator('CHN', 1)
    generator('CHN?')
    assert generator() == str(1)
    generator('OUTPUT', 'OFF')

    if seconds:
        period = 1 / frequency
        width = period * duty
        log('set', f'{width}s {period}s {level[0]}V-{level[1]}V')
    else:
        duty *= 100
        log('set', f'{frequency}Hz {duty}% {level[0]}V-{level[1]}V')

    generator('WAVE', 'PULSE')

    if seconds:
        generator('PULSWID', width)
        generator('PULSPER', period)
    else:
        generator('PULSSYMM', duty)
        generator('PULSFREQ', frequency)

    generator('LOLVL', level[0])
    generator('HILVL', level[1])

    generator('OUTPUT', 'ON')

def ohm():

    multmeter('OHMS')
    multmeter('MODE?')
    mode = multmeter()
    assert 'OHM' in mode.upper(), str(mode)

    multmeter('READ?')
    value = float(multmeter().split(' ')[0])
    log('read', str(value) + 'Ω')

    return value

if __name__ == '__main__':

    log = Logger()

    try:

        generator = LxiDevice.find('TGF4042').open()
        multmeter = LxiDevice.find('1908P').open()

        generator('*IDN?')
        log('ping', generator())

        multmeter('*IDN?')
        log('ping', multmeter())

        freq = 1
        duty = [i / 10 for i in range(1, 10)]

        for _ in duty:

            pwm(freq, _)
            generator.sleep(1e-3)

            for i in range(3):

                ohm()
                multmeter.sleep(1e-3)

    except Exception as e:
        log('error' + str(e))
        log(None, repr(e))
