# #%% console  shift enter
import socket


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


def SendFileIndex(Client):
    f = open("index.html", "rb")
    L = f.read()
    header = """HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-length: %d\r\n\r\n"""%len(L)
    print("----------- HTTP response index.html: ")
    print(header)
    header += L.decode()
    header += "\n\n\n"
    Client.send(bytes(header, 'utf-8'))
    f.close()

def MovePageIndex(Client):
    header = """HTTP/1.1 301 Moved Permanently\r\nLocation: http://127.0.0.1:1235/index.html \n\n\n"""
    print(">")
    print("----------- HTTP response move Index.html:")
    print(header)
    Client.send(bytes(header, 'utf-8'))


def MoveHomePage(Server, Client, Request):
    if "GET /index.html HTTP/1.1" in Request:
        SendFileIndex(Client)
        Server.close()
        return True
    if "GET / HTTP/1.1" in Request:
        MovePageIndex(Client)
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


def Move404(Server, Client):
    header = """HTTP/1.1 301 Moved Permanently\r\nLocation: http://127.0.0.1:1236/404.html \n\n\n"""
    print("HTTP response: ")
    print(header)
    Client.send(bytes(header, "utf-8"))
    Server.close()


def SendFile404(Client):
    f = open("404.html", "rb")
    L = f.read()
    header = """HTTP/1.1 404 Not Found\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Encoding: UTF-8\r\nContent-Length: %d\r\n\r\n"""%len(L)
    print("HTTP response file 404.html: ")
    print(header)
    header += L.decode()
    header += "\n\n\n"
    Client.send(bytes(header, 'utf-8'))


def Send404(Server, Client):
    Server = createServer("localhost", 1236)
    Client, Request = ReadHTTPRequest(Server)
    print("HTTP Request: ")
    print(Request)
    if "GET /404.html HTTP/1.1" in Request:
        SendFile404(Client)
    Server.close()


def MoveInfo(Server, Client):
    header = """HTTP/1.1 301 Moved Permanently\r\nLocation: http://127.0.0.1:1236/info.html \n\n\n
    """
    print("HTTP response: ")
    print(header)
    Client.send(bytes(header, 'utf-8'))
    Server.close()


def SendFileInfo(Client):
    f = open("info.html", "rb")
    L = f.read()
    header = """HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Encoding: UTF-8\r\nContent-Length: %d\r\n\r\n"""%len(L)
    print("-------------HTTP response  info.html: ")
    print(header)
    header += L.decode()
    header += "\n\n\n"
    Client.send(bytes(header, 'utf-8'))


def SendInfo(Server, Client):
    Server = createServer("localhost", 1236)
    Client, Request = ReadHTTPRequest(Server)
    print("HTTP Request: ")
    print(Request)
    if "GET /info.html HTTP/1.1" in Request:
        SendFileInfo(Client)
    Server.close()


if __name__ == "__main__":
    print("Part 1: Return our homepage when a client visit our Server")
    # 1. Create server
    Server = createServer("localhost", 1234)

    # 2. Client connect to Server
    Client, Request = ReadHTTPRequest(Server)
    print("-------------HTTP request: ")
    print(Request)

    # 3. Response then close server
    MoveHomePage(Server, Client, Request)

    print("Part 2: Username and password handling")
    Server = createServer("localhost", 10000)
    Client, Request = ReadHTTPRequest(Server)
    print("-------------- HTTP request: ")
    print(Request)
    if CheckPass(Request) == True:
        MoveInfo(Server, Client)
        SendInfo(Server, Client)
    else:
        Move404(Server, Client)
        Send404(Server, Client)
