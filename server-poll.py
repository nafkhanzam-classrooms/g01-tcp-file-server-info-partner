import socket
import struct
import json
import os
import sys
import threading
import select

SERVER_DIR = "server_files"
os.makedirs(SERVER_DIR, exist_ok=True)

SEND_LOCK = threading.Lock()

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
    
    with SEND_LOCK:
        try:
            sock.sendall(msglen + msg_data)
            if file_path:
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        sock.sendall(chunk)
        except Exception as e:
            print(f"Send error: {e}")

def handle_message(conn, msg, clients):
    cmd = msg.get("cmd")
    
    if cmd == "list":
        files = os.listdir(SERVER_DIR)
        files_str = "\n".join(files) if files else "No files on server."
        send_msg(conn, {"cmd": "msg", "text": f"-- Files on server --\n{files_str}\n-------------------"})
        
    elif cmd == "upload":
        filename = msg.get("filename")
        filesize = msg.get("file_size")
        filename = os.path.basename(filename)
        filepath = os.path.join(SERVER_DIR, filename)
        
        print(f"[*] Receiving upload {filename} ({filesize} bytes)...")
        with open(filepath, 'wb') as f:
            remaining = filesize
            while remaining > 0:
                chunk_size = min(4096, remaining)
                chunk = conn.recv(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                remaining -= len(chunk)
        
        send_msg(conn, {"cmd": "msg", "text": f"Upload of {filename} successful."})
        print(f"[+] Upload complete: {filename}")
        
    elif cmd == "download":
        filename = msg.get("filename")
        filename = os.path.basename(filename)
        filepath = os.path.join(SERVER_DIR, filename)
        
        if os.path.exists(filepath):
            filesize = os.path.getsize(filepath)
            print(f"[*] Sending file {filename} ({filesize} bytes)...")
            send_msg(conn, {"cmd": "file", "filename": filename, "file_size": filesize}, filepath)
        else:
            send_msg(conn, {"cmd": "msg", "text": f"Error: File {filename} not found."})
            
    elif cmd == "broadcast":
        text = msg.get("text")
        addr = conn.getpeername()
        broadcast_text = f"[{addr[0]}:{addr[1]}] {text}"
        print(f"Broadcast: {broadcast_text}")
        
        for client in list(clients):
            if client != conn:
                try:
                    send_msg(client, {"cmd": "msg", "text": broadcast_text})
                except Exception as e:
                    print(f"Failed to send to a client: {e}")
                    if isinstance(clients, set) and client in clients:
                        clients.remove(client)
                    elif isinstance(clients, list) and client in clients:
                        clients.remove(client)

def main():
    if not hasattr(select, "poll"):
        print("[!] The select.poll() syscall is not supported on Windows.")
        print("[!] Please run this script on Linux, macOS, or WSL.")
        sys.exit(1)

    if len(sys.argv) != 3:
        print("Usage: python server-poll.py <host> <port>")
        sys.exit(1)
        
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[*] Poll server listening on {host}:{port}")
    
    poller = select.poll()
    poller.register(server, select.POLLIN)
    
    fd_to_socket = {server.fileno(): server}
    clients = set()
    
    while True:
        try:
            events = poller.poll()
            for fd, flag in events:
                s = fd_to_socket[fd]
                
                # Check for read events
                if flag & (select.POLLIN | select.POLLPRI):
                    if s is server:
                        conn, addr = server.accept()
                        print(f"[+] Connected to {addr}")
                        poller.register(conn, select.POLLIN)
                        fd_to_socket[conn.fileno()] = conn
                        clients.add(conn)
                    else:
                        try:
                            msg = recv_msg(s)
                            if not msg:
                                print(f"[-] Disconnected from {s.getpeername()}")
                                poller.unregister(s)
                                del fd_to_socket[s.fileno()]
                                clients.remove(s)
                                s.close()
                                continue
                            handle_message(s, msg, clients)
                        except Exception as e:
                            print(f"[-] Error or Disconnect: {e}")
                            try:
                                poller.unregister(s)
                            except:
                                pass
                            if s.fileno() in fd_to_socket:
                                del fd_to_socket[s.fileno()]
                            if s in clients:
                                clients.remove(s)
                            s.close()
                elif flag & (select.POLLERR | select.POLLHUP | select.POLLNVAL):
                    print(f"[-] Disconnected (poll error)")
                    try:
                        poller.unregister(s)
                    except:
                        pass
                    if s.fileno() in fd_to_socket:
                        del fd_to_socket[s.fileno()]
                    if s in clients:
                        clients.remove(s)
                    s.close()
        except KeyboardInterrupt:
            print("\n[*] Exiting...")
            for c in clients:
                c.close()
            server.close()
            sys.exit(0)

if __name__ == "__main__":
    main()
