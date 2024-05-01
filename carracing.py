import pygame
import time
import math
from utils import resize_image,blit_rotate_center,blit_text_center
pygame.font.init()

grass=resize_image(pygame.image.load("grass.jpg"),2.5)
track=resize_image(pygame.image.load("track.png"),0.9)

track_border=resize_image(pygame.image.load("track-border.png"),0.9)
track_border_mask=pygame.mask.from_surface(track_border)
finish=pygame.image.load("finish.png")
finish_mask=pygame.mask.from_surface(finish)
finish_position=(130,250)

red_car=resize_image(pygame.image.load("red-car.png"),0.55)
green_car=resize_image(pygame.image.load("green-car.png"),0.55)

width,height=track.get_width(), track.get_height()
WIN=pygame.display.set_mode((width,height))
pygame.display.set_caption("CAR RACE!")

MAIN_FONT=pygame.font.SysFont("helvetica",44)

FPS = 60
PATH=[(155, 163), (160, 103), (134, 72), (87, 92), (66, 224), (60, 350), (62, 409), (58, 456), (79, 500), (109, 535), (285, 707), (315, 727), (347, 726), (409, 550), (423, 500), (550, 494), (596, 560), (604, 674), (654, 725),
                    (714, 718), (733, 602), (733, 478), (714, 390), (656, 362), (461, 357), (401, 315), (434, 251), (604, 238), (701, 220), (722, 109), (598, 69), (404, 74), (325, 75), (273, 137), (284, 247), (273, 370), (190, 388), (170, 260)]
class GameData:
    LEVELS=3 

    def _init_(self,level=1):
        self.level=level
        self.launched=False
        self.level_start_time=0

    def successive_level(self):
        self.level+=1
        self.launched=False

    def restart(self):
        self.level=1
        self.launched=False
        self.level_start_time=0

    def game_over(self):
        return self.level>self.LEVELS
    
    def start_level(self):
        self.launched=True
        self.level_start_time=time.time()

    def obtain_level_duration(self):
        if not self.launched:
            return 0
        return round(time.time()- self.level_start_time)
    
class Car:
    def _init_(self,max_speed,rot_speed):
        self.img=self.IMG
        self.max_speed=max_speed
        self.speed=0
        self.rot_speed=rot_speed
        self.angle=0
        self.a, self.b = self.INITIAL_POS
        self.acc=0.1
      
    def rotation(self,left=False,right=False):
        if left:
            self.angle+=self.rot_speed
        elif right:
            self.angle-=self.rot_speed

    def draw(self,win):
        blit_rotate_center(win,self.img,(self.a,self.b),self.angle)

    def move_fwd(self):
        self.speed=min(self.speed + self.acc,self.max_speed)
        self.move()

    def move_bwd(self):
        self.speed=max(self.speed- self.acc,-self.max_speed/2)
        self.move()    

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians)*self.speed
        horizontal = math.sin(radians)*self.speed

        self.b-=vertical
        self.a-=horizontal

    def collision(self, mask, a=0, b=0):
        car_mask=pygame.mask.from_surface(self.img)
        offset=(int(self.a - a),int(self.b - b))
        poi=mask.overlap(car_mask,offset)
        return poi
    
    def restart(self):
        self.a,self.b=self.INITIAL_POS
        self.angle=0
        self.speed=0


class GamerCar(Car):
    IMG=red_car
    INITIAL_POS=(180,200)

    def decrease_speed(self):
        self.speed = max(self.speed - self.acc/2,0)
        self.move()
    
    def bounce(self):
        self.speed=-self.speed
        self.move()

class ComputerCar(Car):
    IMG=green_car
    INITIAL_POS=(150,200)

    def _init_(self,max_speed,rot_speed,path=[]):
        super()._init_(max_speed,rot_speed)
        self.path=path
        self.current_point=0
        self.speed=max_speed

    def sketch_points(self,win):
        for point in self.path:
            pygame.draw.circle(win,(255,0,0),point,5)
    
    def draw(self,win):
        super().draw(win)
        #self.draw_points(win)
    
    def measure_angle(self):
        target_a,target_b=self.path[self.current_point]
        a_diff=target_a-self.a
        b_diff=target_b-self.b

        if b_diff==0:
            desired_radian_angle=math.pi/2

        else:
            desired_radian_angle=math.atan(a_diff/b_diff)

        if target_b>self.b:
            desired_radian_angle+=math.pi

        angle_difference=self.angle-math.degrees(desired_radian_angle)
        if angle_difference>=180:
            angle_difference-=360

        if angle_difference>0:
            self.angle-=min(self.rot_speed,abs(angle_difference))
        else:
            self.angle+=min(self.rot_speed,abs(angle_difference))

    def update_path_point(self):
        target=self.path[self.current_point]
        rect=pygame.Rect(self.a,self.b,self.img.get_width(),self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point+=1


        
    def move(self):
        if self.current_point>=len(self.path):
            return
        
        self.measure_angle()
        self.update_path_point()
        super().move()
 
    def successive_level(self,level):
        self.restart()
        self.speed=self.max_speed+(level-1)*0.2
        self.current_point=0
        

def draw(win,images,gamer_car,computer_car,game_data):
    for img,pos in images:
        win.blit(img,pos)

    level_text=MAIN_FONT.render(f"Level {game_data.level}" , 1, (255,0,0))
    win.blit(level_text, (10,height-level_text.get_height()-110))

    time_text=MAIN_FONT.render(f"Time: {game_data.obtain_level_duration()}" , 1, (255,0,0))
    win.blit(time_text, (10,height-time_text.get_height()-70))

    gamer_car.draw(win)
    computer_car.draw(win)
    pygame.display.update()

def move_player(gamer_car):
    keys= pygame.key.get_pressed()
    moved=False

    if keys[pygame.K_a]:
        gamer_car.rotation(left=True)
    if keys[pygame.K_d]:
        gamer_car.rotation(right=True)
    if keys[pygame.K_w]:
        moved=True
        gamer_car.move_fwd()
    if keys[pygame.K_s]:
        moved=True
        gamer_car.move_bwd()

    if not moved:
      gamer_car.decrease_speed()


def  manage_collision(gamer_car,computer_car,game_data):
    if gamer_car.collision(track_border_mask)!=None:
        gamer_car.bounce()

    computer_finish_collide=computer_car.collision(finish_mask,*finish_position)
    if computer_finish_collide!=None:
        blit_text_center(WIN,MAIN_FONT,"OOPS!!! You lost!")
        pygame.display.update()
        pygame.time.wait(5000)
        game_data.restart()
        gamer_car.restart()
        computer_car.restart()


    gamer_finish_collide=gamer_car.collision(finish_mask,*finish_position)
    if gamer_finish_collide!=None:
        if gamer_finish_collide[1]==0:
            gamer_car.bounce()
        else:
            game_data.successive_level()
            gamer_car.restart()
            computer_car.successive_level(game_data.level)

run= True
clock=pygame.time.Clock()
images=[(grass,(0,0)),(track,(0,0)),(finish,finish_position),(track_border,(0,0))]
gamer_car=GamerCar(4,4)
computer_car=ComputerCar(0.5,4,PATH)
game_data=GameData()

while run:
    clock.tick(FPS)
    draw(WIN,images,gamer_car,computer_car,game_data)

    while not game_data.launched:
        blit_text_center(WIN,MAIN_FONT,f"Press any key to start level {game_data.level}!")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                break
            
            if event.type==pygame.KEYDOWN:
                game_data.start_level()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
   
        
    move_player(gamer_car)
    computer_car.move()

    manage_collision(gamer_car,computer_car,game_data)

    if game_data.game_over():
        blit_text_center(WIN,MAIN_FONT,"HURRAH!!! YOU WON THE GAME!")
        pygame.time.wait(5000)
        game_data.restart()
        gamer_car.restart()
        computer_car.restart()
            


pygame.quit()