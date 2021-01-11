# #%% console shift enter
import socket
import os

IP = ""

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
    if "GET / HTTP/1.1" in Request:
        MoveToPage(Client, "http://" + IP + ":1234/index.html")

        Client, Request = ReadHTTPRequest(Server)
        print("------------ HTTP request:")
        print(Request)
        MoveHomePage(Server, Client, Request)
        return True
    if "GET /index.html HTTP/1.1" in Request:
        SendFile(Client, GetFileNameFromRequest(Request))  # index.html
        ReadRequestAndSendFile(Server, False)  # styleIndex.css
        ReadRequestAndSendFile(Server, False)  # favicon.ico
        return True


def CheckPass(Request):
    if  "POST" in Request and "HTTP/1.1" in Request and "user-name=admin&password=admin" in Request:
        return True
    else:
        return False


def GetFileNameFromRequest(Request):
    return Request[5:Request.find(" HTTP/1.1")]  # GET /files.html HTTP/1.1...

def GetExtension(fileName):
    splittedFileName = fileName.split('.')
    return splittedFileName[len(splittedFileName) - 1]  #lấy phần sau dấu chấm cuối cùng

def GetFileNameOnly(fileName):
    extension = GetExtension(fileName)
    result = fileName.replace("."+extension, '')
    return result

def MoveToPage(Client, location):
    header = "HTTP/1.1 301 Moved Permanently\r\nLocation: "
    header += location
    header += "\n\n\n"
    print("HTTP response: ")
    print(header)
    Client.send(bytes(header, 'utf-8'))
    

def ReadRequestAndSendFile(Server, isChunked):

    Client, Request = ReadHTTPRequest(Server)
    print("-------------HTTP Request: ")
    print(Request)

    if "GET /" in Request and " HTTP/1.1" in Request:
        fileName = GetFileNameFromRequest(Request)
        if isChunked:
            SendChunkedFile(Client, fileName)
        else:
            SendFile(Client, fileName)

def SendFile(Client, fileName):
    L = ""
    if fileName == "files.html":
        #nếu file cần gửi là files.html thì hiện các file theo thư mục download
        L = """<!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8" />
                    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                    <link rel="stylesheet" href="styleFiles.css" />
                    <title>Files</title>
                </head>
                <body>
                    <h2>List files</h2>
                    <ul>"""
        for filename in os.listdir("download"):
            L += "<li><a href=\"download/"+filename+"\" download=\""+filename+"\">"
            L += GetFileNameOnly(filename)+" ("+GetExtension(filename)+")</a></li>\n"
        L += "</ul></body></html>"
        print(L)
        L = L.encode('utf-8')
    else:
        f = open(fileName, "rb")
        L = f.read()
        f.close()

    extension = GetExtension(fileName)

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

def SendChunkedFile(Client, fileName):
    extension = GetExtension(fileName)

    header = "HTTP/1.1 200 OK\r\nContent-Type: "
    extensionMIMEType = {
                'txt':'text/plain',
                'png':'image/png',
                'jpg':'image/jpeg',
                'jpeg':'image/jpeg',
                'pptx':'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                'ppt':'application/vnd.ms-powerpoint',
                'pdf':'application/pdf',
                'mp3':'audio/mpeg',
                'mp4':'video/mp4',
                'gif':'image/gif',
                'wav':'audio/wav',
                'docx':'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'xls':'application/vnd.ms-excel',
                'xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
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
        fileBytes += ("%X\r\n" % BUFFER_SIZE).encode('utf-8') #kích thước của chunk phải truyền dưới dạng hex
        fileBytes += currentChunk
        fileBytes += "\r\n".encode('utf-8')
        currentChunk = f.read(BUFFER_SIZE)
    f.close()
    #phần còn lại
    remainingSize = len(currentChunk)
    if remainingSize > 0:
        fileBytes += ("%X\r\n" % remainingSize).encode('utf-8')
        fileBytes += currentChunk
        fileBytes += "\r\n".encode('utf-8')
    fileBytes += ("%X\r\n" % 0).encode('utf-8')   #chunk kết thúc "0\r\n"

    Client.send(header.encode('utf-8') + fileBytes + "\r\n".encode('utf-8'))

def CheckButtonPress(Request):
    if  "POST" in Request and "HTTP/1.1" in Request:
        return True
    else:
        return False

if __name__ == "__main__":

    print("Enter your IP address: ")
    IP = input()
    print("Part 1: Return our homepage when a client visit our Server")
    # 1.  Create server
    Server = createServer(IP, 1234)

    # 2.  Client connect to Server
    Client, Request = ReadHTTPRequest(Server)
    print("-------------HTTP request: ")
    print(Request)

    # 3.  Response then close server
    MoveHomePage(Server, Client, Request)

    print("Part 2: Username and password handling")
    Client, Request = ReadHTTPRequest(Server)
    print("-------------- HTTP request: ")
    print(Request)

    if CheckPass(Request) == True:
        MoveToPage(Client, "http://" + IP + ":1234/info.html")
        
        ReadRequestAndSendFile(Server, False) #info.html
        ReadRequestAndSendFile(Server, False) #styleInfo.css
        # 3 cái request dưới đây là ch.png, qd.png và favicon.ico, nhưng thứ tự
                                                     # không giữ nguyên mỗi lần chạy
        ReadRequestAndSendFile(Server, False)
        ReadRequestAndSendFile(Server, False)
        ReadRequestAndSendFile(Server, False)
        
        Client, Request = ReadHTTPRequest(Server)
        print("-------------- HTTP request: ")
        print(Request)
        if CheckButtonPress(Request) == True:
            MoveToPage(Client, "http://" + IP + ":1234/files.html")
            
            ReadRequestAndSendFile(Server, False)   #files.html
            ReadRequestAndSendFile(Server, False)   #styleFiles.css
            ReadRequestAndSendFile(Server, False)   #favicon.ico
            while True:
                ReadRequestAndSendFile(Server, True) #gửi file được bấm theo kiểu chunked
        
    else:
        MoveToPage(Client, "http://" + IP + ":1234/404.html")

        ReadRequestAndSendFile(Server, False)  #404.html
        ReadRequestAndSendFile(Server, False)  #style404.css

    Server.close()
        