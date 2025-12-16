from machine import Pin, I2S
import struct, math, time, json

# -------------------------
# PIN
# -------------------------
sck_pin = Pin(32)
ws_pin  = Pin(25)
sd_pin  = Pin(33)

sample_rate = 8000
CAL_OFFSET = 110.8
IGNORE_SAMPLES = 25
buffer = bytearray(512)


audio_in = I2S(
    0,
    sck=sck_pin,
    ws=ws_pin,
    sd=sd_pin,
    mode=I2S.RX,
    bits=32,
    format=I2S.MONO,
    rate=sample_rate,
    ibuf=4096
)


def compute_dbfs(buf, nbytes):
    if nbytes <= 0:
        return -120.0
    samples = nbytes // 4
    if samples == 0:
        return -120.0

    data = struct.unpack("<" + "i"*samples, buf[:nbytes])
    s2 = sum((v >> 4) ** 2 for v in data)
    rms = math.sqrt(s2 / samples)

    if rms == 0:
        return -120.0

    full_scale = (2 ** 31) - 1
    return 20 * math.log10(rms / full_scale)

async def dbspl_json():

    for _ in range(IGNORE_SAMPLES):
        audio_in.readinto(buffer)
        time.sleep_ms(5)
    # Læs én måling
    n = audio_in.readinto(buffer)
    if n and n > 0:

        I2S.shift(buf=buffer, bits=32, shift=4)

        dBFS = compute_dbfs(buffer, n)
        dBSPL = dBFS + CAL_OFFSET

        data_to_send = {
            "current_dBSPL": round(dBSPL, 1)
            }

        wifi_payload = json.dumps(data_to_send)

        print("JSON:", wifi_payload)

        return wifi_payload

    return None





