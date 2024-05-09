import socket

# Tạo socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Lấy hostname và IP của server
host = "192.168.1.81"
port = 12345  # Cổng của server

# Kết nối tới server
client_socket.connect((host, port))
print(f'Connected to {host}:{port}')

# Nhận thông báo kết nối thành công từ server
success_message = client_socket.recv(1024)
print(success_message.decode())

# Gửi dữ liệu tới server
message = b'Hello from client!'
client_socket.sendall(message)

# Nhận phản hồi từ server
data = client_socket.recv(1024)
print(f'Received: {data.decode()}')

# Đóng kết nối
client_socket.close()