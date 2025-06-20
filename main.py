import random
import time
import os

model = "RAGEVOLT R1"

def gb(x): return x * 1024**3
def mb(x): return x * 1024**2
def fmt(byte): return f"{byte / (1024**3):.2f} GB"

class CPU:
    def __init__(self, name="Ryzen 9 9950X", cores=16, ghz=5.7):
        self.name = name
        self.cores = cores
        self.ghz = ghz
        self.cycles = 0
        self.tdp = 170

    def execute(self, instructions):
        cycles = int(instructions // (self.ghz * 1e6))
        self.cycles += cycles
        print(f"🧠 CPU executed {instructions} instructions | Cycles: {cycles} | Total: {self.cycles}")
        return self.tdp * (cycles / 1e6)

class GPU:
    def __init__(self, model="NVIDIA GeForce RTX 5090", vram_gb=24):
        self.model = model
        self.vram = gb(vram_gb)
        self.used = 0

    def render(self, raytracing=True):
        usage = random.randint(mb(512), mb(2048))
        if self.used + usage > self.vram:
            print("💥 VRAM OVERLOAD!")
            return
        self.used += usage
        print(f"🎮 {self.model} rendered frame (RTX={raytracing}) | VRAM: {fmt(self.used)} / {fmt(self.vram)}")

    def clear(self):
        freed = random.randint(mb(256), mb(1024))
        self.used = max(0, self.used - freed)
        print(f"🧹 VRAM cleared | Now: {fmt(self.used)}")

class RAM:
    def __init__(self, capacity_gb=64):
        self.total = gb(capacity_gb)
        self.used = 0

    def alloc(self, amount):
        if self.used + amount > self.total:
            raise MemoryError("💥 RAM FULL!")
        self.used += amount
        print(f"📦 RAM Allocated: {fmt(amount)} | Used: {fmt(self.used)} / {fmt(self.total)}")

    def free(self, amount):
        self.used = max(0, self.used - amount)
        print(f"📤 RAM Freed: {fmt(amount)} | Now: {fmt(self.used)}")

class VirtualDisk:
    def __init__(self, capacity_gb=1024):
        self.capacity = capacity_gb * 1024**3
        self.used = 0

    def write(self, size_bytes):
        if self.used + size_bytes > self.capacity:
            raise IOError("💽 Disk Full (Virtual)!")
        self.used += size_bytes
        print(f"💽 Virtual Disk Write: {fmt(size_bytes)} | Used: {fmt(self.used)} / {fmt(self.capacity)}")

    def delete(self, size_bytes):
        self.used = max(0, self.used - size_bytes)
        print(f"🗑️ Virtual Disk Deleted: {fmt(size_bytes)} | Used: {fmt(self.used)} / {fmt(self.capacity)}")

class PSU:
    def __init__(self, watt=850):
        self.max_watt = watt

    def draw(self, cpu_watt, gpu_watt):
        total = cpu_watt + gpu_watt
        if total > self.max_watt:
            raise RuntimeError(f"🔥 PSU OVERLOAD! Drawing {total}W")
        print(f"⚡ PSU draw: {total}W / {self.max_watt}W")

class PyREALOS:
    def __init__(self):
        self.cpu = CPU()
        self.gpu = GPU()
        self.ram = RAM()
        self.disk = VirtualDisk(1024)
        self.psu = PSU()

    def boot(self):
        print("🟢 Booting OS...")
        self.cpu.execute(5_000_000)
        self.ram.alloc(mb(512))
        self.disk.write(mb(256))
        print("✅ System Ready.\n")

    def shell(self):
        while True:
            try:
                cmd = input("shell $ ").strip().lower()
                if cmd == "help":
                    print("Commands: help, status, play, shutdown, vram, ramfree, diskdel, gpuinfo, benchmark")
                elif cmd == "status":
                    print(f"🧠 CPU Cycles: {self.cpu.cycles}")
                    print(f"🎮 VRAM Used: {fmt(self.gpu.used)} / {fmt(self.gpu.vram)}")
                    print(f"📦 RAM Used: {fmt(self.ram.used)} / {fmt(self.ram.total)}")
                    print(f"💽 Disk Used: {fmt(self.disk.used)} / {fmt(self.disk.capacity)}")
                elif cmd == "play":
                    self.cpu.execute(20_000_000)
                    self.gpu.render()
                    self.ram.alloc(mb(8192))
                    self.disk.write(mb(1024))
                    self.psu.draw(cpu_watt=150, gpu_watt=350)
                elif cmd == "shutdown":
                    print("🔻 System shutting down...")
                    self.gpu.clear()
                    self.ram.free(mb(8192))
                    self.disk.delete(mb(512))
                    break
                elif cmd == "vram":
                    print(f"🎮 VRAM Usage: {fmt(self.gpu.used)} / {fmt(self.gpu.vram)}")
                elif cmd == "ramfree":
                    amt = mb(1024)
                    self.ram.free(amt)
                elif cmd == "diskdel":
                    amt = mb(512)
                    self.disk.delete(amt)
                elif cmd == "gpuinfo":
                    print(f"🎮 GPU Model: {self.gpu.model}")
                    print(f"🧩 VRAM Total: {fmt(self.gpu.vram)}")
                    print(f"📊 VRAM Used: {fmt(self.gpu.used)}")
                elif cmd == "benchmark":
                    print("🧪 Starting benchmark...")
                    self.cpu.execute(100_000_000)
                    for _ in range(3): 
                        self.gpu.render()
                    self.ram.alloc(mb(4096))
                    self.disk.write(mb(2048))
                    self.psu.draw(cpu_watt=200, gpu_watt=400)
                    print("✅ Benchmark completed!")
                else:
                    print("❌ Unknown command.")
            except Exception as e:
                print("⚠️ Error:", e)

if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    system = PyREALOS()
    system.boot()
    system.shell()
