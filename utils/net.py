import socket
import struct
import select

config = open('utils/config.txt')

IP = socket.gethostbyname(socket.gethostname())
PORT = int(config.readline().strip(' PORT= \n'))

class Host():
    def __init__(self):
        self.message = '' 
        self.ready_to_send = True
        
    def connect(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server.bind((IP, PORT))
        except socket.error:
            self.message = 'Invalid port'
            return False

        self.server.setblocking(False)
        self.server.settimeout(1)
        self.server.listen(1)
        try:
            self.server, addr = self.server.accept()
            return True
        except socket.timeout:
            self.message = 'Waiting for robot'


    def send_data(self, data):
        if data:
            buffer = struct.pack('!3f 3f 3f', *sum(data, ()))
            self.server.sendall(buffer)
            return buffer
        else:
            return data

    def get_data(self):
        if select.select([self.server], [], [], 0)[0]:
            try:
                return self.server.recv(36)
            except:
                print('Błąd odbierania')


def point(xy,z):
    return [xy[0], xy[1], z]
    

class PointHandler:
    def __init__(self,idle_offset):
        self.point_buffer = []
        self.idle_offset = idle_offset
        self.special_active = False

    def follow(self, draw_feedback, z):
        if draw_feedback != None:
            action = draw_feedback[0]
            xy = draw_feedback[1]
            match action:
                case 0:
                    self.add_starting(point(xy, z))
                case 1:
                    self.add(point(xy, z))
                case 2:
                    self.add_ending(point(xy, z))

    def add_starting(self, cords):        
        self.point_buffer.append(([cords[0], cords[1], cords[2] + self.idle_offset], False))
        self.point_buffer.append((cords, False))

    def add(self, cords):
        self.point_buffer.append((cords, True))

    def add_ending(self, cords):
        self.point_buffer.append((cords, False))
        self.point_buffer.append(([cords[0], cords[1], cords[2] + self.idle_offset], False))

    def fetch(self, z_tune):
        raw_points = []
        points_to_send = []
        if self.point_buffer:
            if not self.point_buffer[0][1]:
                points_to_send.extend([(self.point_buffer[0][0][0],               #x
                                        self.point_buffer[0][0][1],               #y
                                        self.point_buffer[0][0][2] + z_tune,)]*3) #z
                raw_points.append(self.point_buffer[0][0])
                del self.point_buffer[0]
                return raw_points, points_to_send
            else:
                batch = []                
                for i in range(min(9, len(self.point_buffer))):
                    if self.point_buffer[i][1]:
                        batch.append(self.point_buffer[i][0])
                    else:
                        break
                raw_points = batch.copy()
                last_point = batch[-1]
                batch_len = len(batch)
                for _ in range(3):
                    if len(batch)>=3:
                        #print("batch: ",batch)
                        points_to_send.append((sum(c[0] for c in batch[:3])/3, #x
                                               sum(c[1] for c in batch[:3])/3, #y
                                               batch[0][2] + z_tune))          #z
                        del batch[:3]
                    else:
                        points_to_send.append((last_point[0],
                                               last_point[1],
                                               last_point[2] + z_tune))
                del self.point_buffer[:batch_len]

                return raw_points, points_to_send
        else:
            return raw_points, points_to_send

    def move_robot(self, canvas, z, host):
        if not self.special_active and not self.point_buffer:
            self.special_active = True
            host.send_data(([(canvas.x, canvas.y, z + 50)]*3))
            
    def test_canvas(self, canvas, z):
        if not self.special_active and not self.point_buffer:
            self.special_active = True
            sequence = (
                (canvas.x, canvas.y, z + self.idle_offset),
                (canvas.x, canvas.y, z),
                (canvas.x + canvas.width, canvas.y, z),
                (canvas.x + canvas.width, canvas.y + canvas.height, z),
                (canvas.x, canvas.y + canvas.height, z),
                (canvas.x, canvas.y, z),
                (canvas.x, canvas.y, z + self.idle_offset),
            )
            for point in sequence:
                self.point_buffer.extend([(point, False)])           

    def clear_canvas(self, canvas):
        if not self.point_buffer:
            canvas.clear()