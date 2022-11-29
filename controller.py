from model import model as m

class Controller():
    def __init__(self) -> None:
        
        self.robots = self.getAllRobot()
        
    def getAllRobot(self) -> list:
        
        robots = []
        response = m.getAllDeviceId()
        for robot in response:
            robots.append(robot['deviceId'])
            
        return robots
        
    
controller = Controller()
print(controller.robots)

