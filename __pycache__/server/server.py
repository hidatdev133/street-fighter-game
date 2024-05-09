import socket

# Tạo socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Lấy hostname và IP
host = "192.168.1.81"
port = 12345  # Cổng mà server lắng nghe

# Liên kết socket với địa chỉ và cổng
server_socket.bind((host, port))

# Lắng nghe kết nối
server_socket.listen(5)
print(f'Server listening on {host}:{port}')

while True:
    # Chấp nhận kết nối
    client_socket, addr = server_socket.accept()
    print(f'Got connection from {addr}')

    # Thông báo khi kết nối thành công
    success_message = b'Connection successful!'
    client_socket.sendall(success_message)

    # Nhận dữ liệu từ client
    data = client_socket.recv(1024)
    print(f'Received: {data.decode()}')

    # Gửi phản hồi cho client
    response = b'Hello from server!'
    client_socket.sendall(response)

    # Đóng kết nối với client
    client_socket.close()