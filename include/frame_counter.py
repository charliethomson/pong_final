
class FrameCounter:
    def __init__(self, framecount):
        self.framecount = framecount
        self.init_framecount = None

    def on_frame(self):
        self.framecount += 1
    
    def get_framerate(self) -> float:
        pass
    
    