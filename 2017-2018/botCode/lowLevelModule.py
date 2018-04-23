#!/usr/bin/env python3

import os
import robomodules as rm
import variables as var
from grid import grid
from low_level.motors import Motors
from messages import MsgType, message_buffers, LightState, PacmanCommand

ADDRESS = os.environ.get("LOCAL_ADDRESS","localhost")
PORT = os.environ.get("LOCAL_PORT", 11295)

FREQUENCY = 60

GRID_VAL = 200

class LowLevelModule(rm.ProtoModule):
    def __init__(self, addr, port):
        self.subscriptions = [MsgType.PACMAN_COMMAND, MsgType.LIGHT_STATE]
        super().__init__(addr, port, message_buffers, MsgType, FREQUENCY, self.subscriptions)
        self.current_command = None
        self.current_location = None
        self.motors = Motors()
        self.current_dir = PacmanCommand.EAST
        
    def _should_turn_left(self, cmd):
        return \
            (self.current_dir == PacmanCommand.NORTH and cmd  == PacmanCommand.WEST) or \
            (self.current_dir == PacmanCommand.SOUTH and cmd  == PacmanCommand.EAST) or \
            (self.current_dir == PacmanCommand.EAST and cmd  == PacmanCommand.NORTH) or \
            (self.current_dir == PacmanCommand.WEST and cmd  == PacmanCommand.SOUTH)

    def _should_turn_right(self, cmd):
        return \
            (self.current_dir == PacmanCommand.NORTH and cmd  == PacmanCommand.EAST) or \
            (self.current_dir == PacmanCommand.SOUTH and cmd  == PacmanCommand.WEST) or \
            (self.current_dir == PacmanCommand.EAST and cmd  == PacmanCommand.SOUTH) or \
            (self.current_dir == PacmanCommand.WEST and cmd  == PacmanCommand.NORTH)

    def _should_reverse(self, cmd):
        return \
            (self.current_dir == PacmanCommand.NORTH and cmd  == PacmanCommand.SOUTH) or \
            (self.current_dir == PacmanCommand.SOUTH and cmd  == PacmanCommand.NORTH) or \
            (self.current_dir == PacmanCommand.EAST and cmd  == PacmanCommand.WEST) or \
            (self.current_dir == PacmanCommand.WEST and cmd  == PacmanCommand.EAST)

    def _move_forward(self):
        self.motors.advance(GRID_VAL)

    def _turn_right(self):
        self.motors.turn_right()
        if self.current_dir == PacmanCommand.EAST:
            self.current_dir = PacmanCommand.SOUTH
        elif self.current_dir == PacmanCommand.SOUTH:
            self.current_dir = PacmanCommand.WEST
        elif self.current_dir == PacmanCommand.WEST:
            self.current_dir = PacmanCommand.NORTH
        else:
            self.current_dir = PacmanCommand.EAST
            
    def _turn_left(self):
        self.motors.turn_left()
        if self.current_dir == PacmanCommand.EAST:
            self.current_dir = PacmanCommand.NORTH
        elif self.current_dir == PacmanCommand.NORTH:
            self.current_dir = PacmanCommand.WEST
        elif self.current_dir == PacmanCommand.WEST:
            self.current_dir = PacmanCommand.SOUTH
        else:
            self.current_dir = PacmanCommand.EAST

    def _turn_around(self):
        #TODO: Turn 180 degrees
        if self.current_dir == PacmanCommand.EAST:
            self.current_dir = PacmanCommand.WEST
        elif self.current_dir == PacmanCommand.NORTH:
            self.current_dir = PacmanCommand.SOUTH
        elif self.current_dir == PacmanCommand.WEST:
            self.current_dir = PacmanCommand.EAST
        else:
            self.current_dir = PacmanCommand.NORTH
    
    def _reverse(self):
        self.motors.reverse(GRID_VAL)

    def _execute_command(self):
        if self.current_command:
            cmd = self.current_command
            print(cmd)
            self.current_command = None
            if cmd == PacmanCommand.STOP:
                self.motors.stop()
                return
            if self._should_turn_left(cmd):
                self._turn_left()
            elif self._should_turn_right(cmd):
                self._turn_right()
            if self._should_reverse(cmd):
                self._reverse()
            else:
                self._move_forward()

    def msg_received(self, msg, msg_type):
        if msg_type == MsgType.PACMAN_COMMAND:
            self.current_command = msg.dir
        elif msg_type == MsgType.LIGHT_STATE:
            self.current_location = (msg.pacman.x, msg.pacman.y)

    def tick(self):
        if self.current_command:
            self.set_frequency(0)
            while True:
                self._execute_command()

    def kill(self):
        self.motors.stop()


def main():
    module = LowLevelModule(ADDRESS, PORT)
    try:
        module.run()
    except KeyboardInterrupt:
        module.kill()
if __name__ == "__main__":
    main()
