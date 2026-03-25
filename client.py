import socket
import threading
import struct
import json
import os
import sys

CLIENT_DIR = "client_files" 

def recv_all(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def recv_msg(sock):
    raw_msglen = recv_all(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    msg_data = recv_all(sock, msglen)
    if not msg_data:
        return None
    return json.loads(msg_data.decode('utf-8'))

def send_msg(sock, msg_dict, file_path=None):
    msg_data = json.dumps(msg_dict).encode('utf-8')
    msglen = struct.pack('>I', len(msg_data))
    sock.sendall(msglen + msg_data)
    
    if file_path:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                sock.sendall(chunk)

def receive_thread(sock):
    while True:
        try:
            msg = recv_msg(sock)
            if not msg:
                print("\n[!] Disconnected from server.")
                os._exit(0)
            
            cmd = msg.get("cmd")
            if cmd == "msg":
                print(f"\n{msg.get('text')}\n> ", end="")
            elif cmd == "file":
                filename = msg.get("filename")
                filesize = msg.get("file_size")
                print(f"\n[+] Receiving file {filename} ({filesize} bytes)...")
                
                filepath = os.path.join(CLIENT_DIR, filename)
                with open(filepath, 'wb') as f:
                    remaining = filesize
                    while remaining > 0:
                        chunk_size = min(4096, remaining)
                        chunk = sock.recv(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        remaining -= len(chunk)
                print(f"[+] Download complete: {filename}\n> ", end="")
        except Exception as e:
            print(f"\n[!] Error receiving data: {e}")
            os._exit(0)

def main():
    if len(sys.argv) != 3:
        print("Usage: python client.py <host> <port>")
        sys.exit(1)
        
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
    except Exception as e:
        print(f"[!] Unable to connect: {e}")
        sys.exit(1)
        
    global CLIENT_DIR
    CLIENT_DIR = f"client_files_{sock.getsockname()[1]}"
    os.makedirs(CLIENT_DIR, exist_ok=True)
    
    print(f"[+] Connected to {host}:{port}")
    print(f"[+] Client directory for files is '{CLIENT_DIR}'")
    print("[+] Commands: /list, /upload <file>, /download <file>")
    print("[+] Any other text will be broadcasted to all clients.")
    
    t = threading.Thread(target=receive_thread, args=(sock,), daemon=True)
    t.start()
    
    while True:
        try:
            text = input("> ")
            if not text:
                continue
                
            if text == "/list":
                send_msg(sock, {"cmd": "list"})
            elif text.startswith("/upload "):
                filename = text.split(" ", 1)[1].strip()
                filepath = os.path.join(CLIENT_DIR, filename)
                if os.path.exists(filepath):
                    filesize = os.path.getsize(filepath)
                    send_msg(sock, {"cmd": "upload", "filename": filename, "file_size": filesize}, filepath)
                    print(f"[*] Uploading {filename}...")
                else:
                    print(f"[!] File {filename} not found in {CLIENT_DIR}")
            elif text.startswith("/download "):
                filename = text.split(" ", 1)[1].strip()
                send_msg(sock, {"cmd": "download", "filename": filename})
            elif text.startswith("/"):
                print("[!] Unknown command")
            else:
                send_msg(sock, {"cmd": "broadcast", "text": text})
                
        except KeyboardInterrupt:
            print("\n[!] Exiting...")
            sock.close()
            sys.exit(0)

if __name__ == "__main__":
    main()
