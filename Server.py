# #%% console shift enter
import socket
import time


def createServer(host, port):
    Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Server.bind((host, port))
    Server.listen(5)  # maximun client at a time
    return Server


def readRequest(Client):
    re = ""
    Client.settimeout(1)
    try:
        re = Client.recv(1024).decode()  # binary to string
        while (re):
            re = re + Client.recv(1024).decode()
    except socket.timeout:
        if not re:
            print("Can't receive data! [Timeout]")
    finally:
        return re


def ReadHTTPRequest(Server):
    re = ""
    while (re == ""):
        Client, address = Server.accept()
        print("Client: ", address, " connected to server")
        re = readRequest(Client)
    return Client, re


def MoveHomePage(Server, Client, Request):
    if "GET /index.html HTTP/1.1" in Request:
        SendFile(Client, Request, GetFileNameFromRequest(Request))  # index.html
        ReadRequestAndSendFile(Server, False)  # styleIndex.css
        Server.close()
        return True
    if "GET / HTTP/1.1" in Request:
        MoveToPage(Server, Client, "http://127.0.0.1:1235/index.html")
        Server.close()

        Server = createServer("localhost", 1235)
        Client, Request = ReadHTTPRequest(Server)
        print("------------ HTTP request:")
        print(Request)
        MoveHomePage(Server, Client, Request)
        return True


def CheckPass(Request):
    if "POST / HTTP/1.1" not in Request:
        return False
    if "user-name=admin&password=admin" in Request:
        return True
    else:
        return False


def GetFileNameFromRequest(Request):
    return Request[5:Request.find(" HTTP/1.1")]  # GET /file.html HTTP/1.1...


def MoveToPage(Server, Client, location):
    header = "HTTP/1.1 301 Moved Permanently\r\nLocation: "
    header += location
    header += "\n\n\n"
    print("HTTP response: ")
    print(header)
    Client.send(bytes(header, 'utf-8'))
    Server.close()


def ReadRequestAndSendFile(Server, isChunked):

    Client, Request = ReadHTTPRequest(Server)
    print("-------------HTTP Request: ")
    print(Request)

    if "GET /" in Request and " HTTP/1.1" in Request:
        fileName = GetFileNameFromRequest(Request)
        if isChunked:
            SendChunkedFile(Client, Request, fileName)
        else:
            SendFile(Client, Request, fileName)


def SendFile(Client, Request, fileName):
    f = open(fileName, "rb")
    L = f.read()
    f.close()
    extension = fileName.split('.')[1]

    header = "HTTP/1.1 200 OK\r\nContent-Type: "
    if extension == "html" or extension == "css":
        header += "text/"
    else:
        header += "image/"
    header += extension
    header += "\r\nContent-Length: %d\r\n\r\n""" % len(L)
    print("-------------HTTP response " + fileName + ": ")
    print(header)

    Client.send(header.encode('utf-8') + L + "\r\n".encode('utf-8'))


def SendChunkedFile(Client, Request, fileName):
    splittedFileName = fileName.split('.')
    # lấy phần sau dấu chấm cuối cùng
    extension = splittedFileName[len(splittedFileName) - 1]

    header = "HTTP/1.1 200 OK\r\nContent-Type: "
    extensionMIMEType = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
                'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                'ppt': 'application/vnd.ms-powerpoint',
                'pdf': 'application/pdf',
                'mp3': 'audio/mpeg',
                'mp4': 'video/mp4',
                'gif': 'image/gif',
                'wav': 'audio/wav',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'xls': 'application/vnd.ms-excel',
                'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }

    header += extensionMIMEType.get(extension)
    header += "\r\nTransfer-Encoding: chunked\r\n\r\n"
    print("-------------HTTP response " + fileName + ": ")
    print(header)

    BUFFER_SIZE = 1024 * 1024
    f = open(fileName, "rb")
    currentChunk = f.read(BUFFER_SIZE)
    fileBytes = "".encode('utf-8')

    while len(currentChunk) == BUFFER_SIZE:
        # kích thước của chunk phải truyền dưới dạng hex
        fileBytes += ("%X\r\n" % BUFFER_SIZE).encode('utf-8')
        fileBytes += currentChunk
        fileBytes += "\r\n".encode('utf-8')
        currentChunk = f.read(BUFFER_SIZE)
    f.close()
    # phần còn lại
    remainingSize = len(currentChunk)
    fileBytes += ("%X\r\n" % remainingSize).encode('utf-8')
    fileBytes += currentChunk
    fileBytes += "\r\n".encode('utf-8')
    fileBytes += ("%X\r\n" % 0).encode('utf-8')  # chunk kết thúc "0\r\n"

    Client.send(header.encode('utf-8') + fileBytes + "\r\n".encode('utf-8'))


def CheckButtonPress(Request):
    if "POST / HTTP/1.1" in Request:
        return True
    else:
        return False


if __name__ == "__main__":
    print("Part 1: Return our homepage when a client visit our Server")
    # 1.  Create server
    Server = createServer("localhost", 1234)

    # 2.  Client connect to Server
    Client, Request = ReadHTTPRequest(Server)
    print("-------------HTTP request: ")
    print(Request)

    # 3.  Response then close server
    MoveHomePage(Server, Client, Request)

    print("Part 2: Username and password handling")
    Server = createServer("localhost", 10000)
    Client, Request = ReadHTTPRequest(Server)
    print("-------------- HTTP request: ")
    print(Request)

    if CheckPass(Request) == True:
        MoveToPage(Server, Client, "http://127.0.0.1:1236/info.html")

        Server = createServer("localhost", 1236)
        ReadRequestAndSendFile(Server, False)  # info.html
        ReadRequestAndSendFile(Server, False)  # styleInfo.css
        # 3 cái request dưới đây là ch.png, qd.png và favicon.ico, nhưng thứ tự không giữ nguyên mỗi lần chạy
        ReadRequestAndSendFile(Server, False)
        ReadRequestAndSendFile(Server, False)
        ReadRequestAndSendFile(Server, False)
        Server.close()

        Server = createServer("localhost", 10000)
        Client, Request = ReadHTTPRequest(Server)
        print("-------------- HTTP request: ")
        print(Request)
        if CheckButtonPress(Request) == True:
            MoveToPage(Server, Client, "http://127.0.0.1:1237/files.html")
            Server = createServer("localhost", 1237)
            ReadRequestAndSendFile(Server, False)  # files.html
            ReadRequestAndSendFile(Server, False)
            ReadRequestAndSendFile(Server, False)  # favicon.ico
            while True:
                # gửi file được bấm theo kiểu chunked
                ReadRequestAndSendFile(Server, True)
        Server.close()

    else:
        MoveToPage(Server, Client, "http://127.0.0.1:1236/404.html")
        Server = createServer("localhost", 1236)
        ReadRequestAndSendFile(Server, False)  # 404.html
        ReadRequestAndSendFile(Server, False)  # style404.css
        Server.close()
