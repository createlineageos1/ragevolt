import random
import os
import socket
import threading

pcmodel = "Ragevolt SNC1"

def gb(x): return x * 1024**3
def mb(x): return x * 1024**2
def fmt(byte): return f"{byte / (1024**3):.2f} GB"

class CPU:
    def __init__(self, name="AMD EPYC 9654", cores=64, ghz=3.2):
        self.name = name
        self.cores = cores
        self.ghz = ghz
        self.cycles = 0
        self.tdp = 360

    def execute(self, instructions):
        cycles = int(instructions // (self.ghz * 1e6))
        self.cycles += cycles
        print(f"🧠 CPU executed {instructions} instructions | Cycles: {cycles} | Total: {self.cycles}")
        return self.tdp * (cycles / 1e6)

class GPU:
    def __init__(self, model="NVIDIA Tesla T4", vram_gb=16):
        self.model = model
        self.vram = gb(vram_gb)
        self.used = 0

    def render(self, raytracing=True):
        usage = random.randint(mb(256), mb(512))
        if self.used + usage > self.vram:
            print("💥 VRAM OVERLOAD!")
            return
        self.used += usage
        print(f"🎮 {self.model} rendered frame (RTX={raytracing}) | VRAM: {fmt(self.used)} / {fmt(self.vram)}")

    def clear(self):
        freed = random.randint(mb(128), mb(256))
        self.used = max(0, self.used - freed)
        print(f"🧹 VRAM cleared | Now: {fmt(self.used)}")

class RAM:
    def __init__(self, capacity_gb=512):
        self.total = gb(capacity_gb)
        self.used = 0

    def alloc(self, amount):
        if self.used + amount > self.total:
            raise MemoryError("💥 sterr: RAM FULL!")
        self.used += amount
        print(f"📦 RAM Alloc: {fmt(amount)} | Used: {fmt(self.used)} / {fmt(self.total)}")

    def free(self, amount):
        self.used = max(0, self.used - amount)
        print(f"📤 RAM Freed: {fmt(amount)} | Now: {fmt(self.used)}")

class VirtualDisk:
    def __init__(self, capacity_gb=50*1024):
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
    def __init__(self, watt=2000):
        self.max_watt = watt

    def draw(self, cpu_watt, gpu_watt):
        total = cpu_watt + gpu_watt
        if total > self.max_watt:
            raise RuntimeError(f"🔥 PSU OVERLOAD! Drawing {total}W")
        print(f"⚡ PSU draw: {total}W / {self.max_watt}W")

class PyREALOS_Server:
    def __init__(self, host='0.0.0.0', port=9999):
        self.cpu = CPU()
        self.gpu = GPU()
        self.ram = RAM()
        self.disk = VirtualDisk()
        self.psu = PSU()
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = True

    def boot(self):
        print("🟢 Booting pyREALOS Server...")
        self.cpu.execute(5_000_000)
        self.ram.alloc(mb(512))
        self.disk.write(mb(256))
        print("✅ Server Ready.\n")

    def handle_client(self, client_socket, address):
        print(f"📡 Client connected: {address}")
        try:
            client_socket.send(b"Welcome to pyREALOS Server. Type 'help' for commands.\n")
        except Exception:
            client_socket.close()
            print(f"📴 Client disconnected early: {address}")
            return

        while self.running:
            try:
                data = client_socket.recv(1024).decode().strip().lower()
                if not data:
                    break
                if data == "help":
                    client_socket.send(b"Commands: help, status, ramalloc, ramfree, diskwrite, diskdelete, shutdown\n")
                elif data == "status":
                    status = (
                        f"🧠 CPU Cycles: {self.cpu.cycles}\n"
                        f"🎮 VRAM Used: {fmt(self.gpu.used)} / {fmt(self.gpu.vram)}\n"
                        f"📦 RAM Used: {fmt(self.ram.used)} / {fmt(self.ram.total)}\n"
                        f"💽 Disk Used: {fmt(self.disk.used)} / {fmt(self.disk.capacity)}\n"
                        f"PC Model: {pcmodel}\n"
                    )
                    client_socket.send(status.encode())
                elif data == "ramalloc":
                    try:
                        self.ram.alloc(mb(1))
                        client_socket.send(b"Allocated 1GB RAM.\n")
                    except MemoryError as e:
                        client_socket.send(str(e).encode() + b"\n")
                elif data == "ramfree":
                    self.ram.free(mb(1))
                    client_socket.send(b"Freed 1GB RAM.\n")
                elif data == "diskwrite":
                    try:
                        self.disk.write(mb(10))
                        client_socket.send(b"Wrote 10GB to disk.\n")
                    except IOError as e:
                        client_socket.send(str(e).encode() + b"\n")
                elif data == "diskdelete":
                    self.disk.delete(mb(5))
                    client_socket.send(b"Deleted 5GB from disk.\n")
                elif data == "shutdown":
                    client_socket.send(b"Shutting down server...\n")
                    self.running = False
                    break
                else:
                    client_socket.send(b"Unknown command.\n")
            except (ConnectionResetError, BrokenPipeError):
                break
            except Exception as e:
                try:
                    client_socket.send(f"Error: {e}\n".encode())
                except Exception:
                    pass
                break
        client_socket.close()
        print(f"📴 Client disconnected: {address}")

    def start_server(self):
        self.boot()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"🚀 Server started on {self.host}:{self.port}")
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                client_thread.daemon = True
                client_thread.start()
            except KeyboardInterrupt:
                print("⚠️ Server interrupted by user.")
                break
        self.server_socket.close()
        print("🛑 Server stopped.")

if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    server = PyREALOS_Server()
    server.start_server()
