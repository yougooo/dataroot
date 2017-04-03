import socket
import os
import io
import sys
import re
import time
import webbrowser
import urllib.parse
from http import HTTPStatus
class SimpleServer:


    enc = sys.getfilesystemencoding()

    weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    monthname = [None,
                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


    def __init__(self, server_address=('', 8000)):
        # Create socket and copy, with default value
        self.server_socket = server_socket = socket.socket()
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(server_address)
        # Queue size
        server_socket.listen(10)
        host, port = self.server_socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port
        self.path = '.'
        self.files_list = os.listdir(self.path)
        self.response_header = []
        self.start_header = """
                                    <!DOCTYPE html>\n
                                    <html lang="en">\n
                                    <head>\n
                                    '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'\n
                                    <title>Directory list for</title>\n
                                    <!-- Latest compiled and minified CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">

    <!-- Optional theme -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous">
     <script src="http://code.jquery.com/jquery-latest.js"></script>
    <!-- Latest compiled and minified JavaScript -->
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>

                                    </head>\n
                                    <body>
                                    <style>
                                    a{
                                    color: black;
                                    text-decorator: none;
                                    }
                                    thead{
                                    background-color: rgba(0, 15, 154, 0.49);
                                    color: white;
                                    }
                                    #head{
                                    text-align: center;
                                    }
                                    body{
                                    overflow-x: auto;
                                    }
                                    #tab{
                                    border: 1px solid rgba(0, 15, 154, 0.7);
                                    position: absolute;
                                    top:150px;
                                    width:300px;
                                    margin-left: 50px;

                                    }
                                    input{
                                    margin-left: 30px;
                                    }
                                    </style>
                                    <script>function poisk(){

        var s = $("#search_all").val();
        console.log(s);

        $.each($("#tab tbody tr"), function() {

            if($(this).text().indexOf(s) === -1) {

                $(this).hide();
            } else {
                $(this).show();
            };
        });
    };</script>
    <div id = "head">
                                    <div class = 'col-xs-6 col-md-6 col-sm-6 col-lg-6'>
                                    <h3>DIRECTORY LIST</h3>
                                      <div class="form-group">

            <div class = "col-sm-6 col-md-6 col-lg-6"><input type="text" class="form-control pull-right" id="search_all" placeholder="Search"></div><div class = "col-sm-6 col-md-6 col-lg-6"><button type="button" class="btn btn-default" onclick = poisk()>Submit</button></div>
        </div></div></div>
                                    <table class='table' id = "tab">\n

                                    <thead><tr><td>Header</td></tr></thead>
                                    <tbody>
                                    """
        self.end_header = """
                                    </tbody>

                                    </table></div>\n

                                    </body>\n
                                    </html>\n
                                """

    def _log_date_time_string(self):
        """
        provided by source python library http.server
        Return the current time formatted for logging.
        """
        now = time.time()
        year, month, day, hh, mm, ss, x, y, z = time.localtime(now)
        s = "%02d/%3s/%04d %02d:%02d:%02d" % (
                day, self.monthname[month], year, hh, mm, ss)
        return s

    """
    def _get_response_header(self, key, val):
        self.response_header.append(('{0}: {1}\r\n'.format(key, val)).encode('utf-8', 'strict'))
    """
    def _get_path(self, request):
        """
        :param request: bytes object with socket info(received date)
        :return: str, file name from request
        """
        # find file name in request, regex way
        pattern = re.compile(r'GET /?(.+) HTTP/1.1')
        result = pattern.search(request.decode('utf-8'))
        if result and result.group(1) == '/':
            # dir with file main.py
            self.path = '.'
        elif result:
            self.path = result.group(1)
        return self.path

    def get_response(self):
        """
        :return: data to client response
        """
        if 'index.html' in self.files_list:
            with open('index.html', 'rU') as f:
                response = f.read()
            return response
        file = self.path.split('/')[-1]
        if os.path.isdir(self.path):
            self.files_list = os.listdir(self.path)
            response = ''.join('<tr><td><a  href="{}">{}</a></td></tr>'.format(file, file) for file in self.files_list)
            return self.start_header + response + self.end_header
        elif file in self.files_list:
            with open(file, 'rU') as f:
                response = f.read()
            return response
        else:
            return b'404 Not Found'

    def send_response(self, client_socket):
        request = client_socket.recv(1024)
        self.path = self._get_path(request)
        data = self.get_response()
        encoded = b'HTTP/1.1 200 OK\r\n' + b'Content-Type: text/html\r\n\r\n' + \
                  data.encode(self.enc, 'surrogateescape')
        f = io.BytesIO()
        f.write(b"".join(self.response_header))
        f.write(encoded)
        f.seek(0)
        client_socket.sendall(f.getvalue())
        self.response_header = []

    def run(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            pid = os.fork()
            if pid == 0:
                self.server_socket.close()
                self.send_response(client_socket)
                client_socket.close()
                os._exit(0)
            else:
                client_socket.close()
if __name__ == '__main__':
    test = SimpleServer(('', 8000))
    test.run()
    webbrowser.open('localhost:{}'.format(test.server_port))
