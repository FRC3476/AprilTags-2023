class UpdateState:

    def __init__(self):
        self.do_cam_update = False

    def schedule_update(self):
        self.do_cam_update = True

    def check_update(self):
        if (self.do_cam_update):
            self.do_cam_update = False
            return True
        else:
            return False
