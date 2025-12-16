import matplotlib.pyplot as plt
import random
import time

plt.ioff()  # Deaktiver interaktiv GUI
fig, ax = plt.subplots()
ax.set_title("Live testmålinger")
ax.set_xlabel("Hz")
ax.set_ylabel("dB")
ax.grid(True)


hz = random.randint(100, 2000)
db = random.randint(50, 200)

ax.cla()
ax.set_title("Live testmålinger")
ax.set_xlabel("Hz")
ax.set_ylabel("dB")
ax.grid(True)
ax.plot(hz, db, 'ro')

# Gem grafen til fil
plt.savefig("live_graf.png")


time.sleep(0.5)
