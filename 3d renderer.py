import pygame,math,copy,random
pygame.init()
screenw,screenh = 2000,1200
screen = pygame.display.set_mode((screenw,screenh))
done = False
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

def text_objects(text, font, col):
    textSurface = font.render(text, True, col)
    return textSurface, textSurface.get_rect()

def write(x,y,text,col,size,screen,center):
    largeText = pygame.font.SysFont("impact", size)
    TextSurf, TextRect = text_objects(text, largeText, col)
    if center:
        TextRect.center = (int(x),int(y))
    else:
        TextRect.x = int(x)
        TextRect.y = int(y)
    screen.blit(TextSurf, TextRect)
    
def pythag3d(p1,p2):
    return ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2+(p1[2]-p2[2])**2)**0.5
def avpoint(points):
    tot = [0,0,0]
    for a in points:
        tot[0]+=a[0]
        tot[1]+=a[1]
        tot[2]+=a[2]
    tot[0]/=len(points)
    tot[1]/=len(points)
    tot[2]/=len(points)
    return tot

def controller(camera,cm):
    speed = 5
    kprs = pygame.key.get_pressed()
    if kprs[pygame.K_w]:
        camera[2]+=speed*math.cos(camera[4])
        camera[0]+=speed*math.sin(camera[4])
    elif kprs[pygame.K_s]:
        camera[2]-=speed*math.cos(camera[4])
        camera[0]-=speed*math.sin(camera[4])
    if kprs[pygame.K_a]:
        camera[2]+=speed*math.cos(camera[4]-math.pi/2)
        camera[0]+=speed*math.sin(camera[4]-math.pi/2)
    elif kprs[pygame.K_d]:
        camera[2]+=speed*math.cos(camera[4]+math.pi/2)
        camera[0]+=speed*math.sin(camera[4]+math.pi/2)
    if kprs[pygame.K_SPACE]: camera[1]-=5
    elif kprs[pygame.K_LSHIFT]: camera[1]+=5

    camera[3]-=cm[1]/1000
    camera[4]+=cm[0]/1000
    if camera[3]>math.pi/2: camera[3] = math.pi/2
    elif camera[3]<-math.pi/2: camera[3] = -math.pi/2    

    return camera

def polydrawer(poly,cam,fl,screen):
    for a in range(len(poly)):
        poly[a][2] = pythag3d(cam,poly[a][3])
    poly.sort(key=lambda x: x[2],reverse=True)
    for a in poly:
        drawpoly(a,cam,fl,screen)
        
def drawpoly(poly,cam,fl,screen):
    scrw = screen.get_width()
    scrh = screen.get_height()
    w = screen.get_width()/2
    h = screen.get_height()/2
    cpoly = []
    for a in poly[1]:
        cpoly.append([a[0]-cam[0],a[1]-cam[1],a[2]-cam[2]])
    apoly = []
    for a in cpoly:
        x0 = a[0]
        y0 = a[1]
        z0 = a[2]

        #rotates for left/right turning
        x1 = x0*math.cos(-cam[4])+z0*math.sin(-cam[4])
        y1 = y0
        z1 = z0*math.cos(-cam[4])-x0*math.sin(-cam[4])

        #rotates for up/down turning
        x2 = x1
        y2 = y1*math.cos(-cam[3])-z1*math.sin(-cam[3])
        z2 = y1*math.sin(-cam[3])+z1*math.cos(-cam[3])

        #rotates world clockwise/anticlockwise
        x3 = x2*math.cos(-cam[5])-y2*math.sin(-cam[5])
        y3 = x2*math.sin(-cam[5])+y2*math.cos(-cam[5])
        z3 = z2
        
        apoly.append([x3,y3,z3])
    npoly = []
    inside = False
    for a in apoly:
        npoly.append([(fl)/(a[2])*(a[0])+w,(fl)/(a[2])*(a[1])+h])
##    print(apoly)
##    for a in npoly:
##        if a[0]<0 or a[1]<0:
##            return

    if poly[2]>40:  #inside:
##        angle = 1-abs(math.atan((poly[1][0][1]-poly[3][1])/(math.sqrt((poly[1][0][0]-poly[3][0])**2+(poly[1][0][2]-poly[3][2])**2)))/math.pi*2)
        angle = poly[4]
        if len(npoly)>2:
            pygame.draw.polygon(screen,[poly[0][0]*angle,poly[0][1]*angle,poly[0][2]*angle],npoly)

def ball_maker(radius,x,y,z,detail,col):
    points = []
    for layer in range(detail+1):
        points.append([])
        for ring in range(detail):
            points[layer].append([x+(math.cos((((layer/detail)*2-1))*(math.pi/2)))*radius*math.cos(((ring/detail)*2-1)*(math.pi)),
                                     y+(radius*math.sin(((layer/detail)*2-1)*(math.pi/2))),
                                     z+(math.cos((((layer/detail)*2-1))*(math.pi/2)))*radius*math.sin(((ring/detail)*2-1)*(math.pi))])
    poly = []
    for l in range(detail):
        for b in range(detail):
            col[2] = int(l/detail*255)
            col[1] = 255-int(l/detail*255)
            col[0] = int(b/detail*255)
            poly.append([copy.copy(col),[points[l][b],points[l][(b+1)%len(points[1])],points[l+1][(b+1)%len(points[1])],points[l+1][b]],0,0])
    return poly

def tube_maker(radius,x,y,z,detail,col,height):
    points = []
    for layer in range(height+1):
        points.append([])
        for ring in range(detail):
            points[layer].append([x+radius*math.cos(((ring/detail)*2-1)*(math.pi)),
                                     y+(radius*((layer/detail)*2-1)),
                                     z+radius*math.sin(((ring/detail)*2-1)*(math.pi))])
    poly = []
    for l in range(height):
        for b in range(detail):
            poly.append([col,[points[l][b],points[l][(b+1)%len(points[1])],points[l+1][(b+1)%len(points[1])],points[l+1][b]],0,0])
    return poly

def bean_maker(radius,x,y,z,detail,col,height):
    points = []
    for layer in range(height+1):
        points.append([])
        for ring in range(detail):
            points[layer].append([x+radius*math.cos(((ring/detail)*2-1)*(math.pi)),
                                     y+(radius*((layer/detail)*2-1)),
                                     z+radius*math.sin(((ring/detail)*2-1)*(math.pi))])
    for layer in range(detail+1):
        points.append([])
        for ring in range(detail):
            points[-1].append([x+(math.cos((((layer/detail)*2-1))*(math.pi/2)))*radius*math.cos(((ring/detail)*2-1)*(math.pi)),
                                     y+(radius*math.sin(((layer/detail)*2-1)*(math.pi/2))),
                                     z+(math.cos((((layer/detail)*2-1))*(math.pi/2)))*radius*math.sin(((ring/detail)*2-1)*(math.pi))])
            if points[-1][-1][1]>y:
                points[-1][-1][1]+=radius*3
            else:
                points[-1][-1][1]-=radius
    poly = []
    col = [0,0,0]
    for l in range(height):
        for b in range(detail):
            col[2] = int(l/height*255)
            col[1] = 255-int(l/height*255)
            col[0] = int(b/detail*255)
            poly.append([col,[points[l][b],points[l][(b+1)%detail],points[(l+1)%height][(b+1)%detail],points[(l+1)%height][b]],0,0])
    for l in range(height,height+detail):
        for b in range(detail):
            poly.append([col,[points[l][b],points[l][(b+1)%detail],points[l+1][(b+1)%detail],points[l+1][b]],0,0])
    return poly

def donut_maker(size,radius,x,y,z,detail,col):
    points = []
    for ring in range(detail+1):
        points.append([])
        angle = (ring/detail)*math.pi*2
        center = [x+math.sin(angle)*size,y,z+math.cos(angle)*size]
        for don in range(detail+1):
            points[-1].append([ center[0]+math.cos(don/detail*math.pi*2)*radius*math.sin(angle)
                               ,center[1]+math.sin(don/detail*math.pi*2)*radius
                               ,center[2]+math.cos(don/detail*math.pi*2)*radius*math.cos(angle)
                               ])
    poly = []
    brightcols = [(226,225,222),(200,191,231),(6,147,41),(217,182,6),(189,28,129)]
    for l in range(detail):
        for b in range(detail):
            #col[0] = int(math.sin(l/detail*math.pi)*255)
            #col[1] = int(math.sin(l/detail*math.pi)*255)
            #col[2] = int(math.sin(b/detail*math.pi)*255)
            col = [237,164,34]
            if points[l][b][1]<y:
                if random.randint(0,10)>5:col = [111,39,20]
                else:
                    if points[l][b][1]<y-10:
                        ran = random.randint(0,100)
                        if ran>40: col = [111,39,20]
                        else: col = brightcols[random.randint(0,len(brightcols)-1)]
                    
            ncol = [col[0]+random.randint(-5,5),col[1]+random.randint(-5,5),col[2]+random.randint(-5,5)]
            #ncol = copy.copy(col)
            poly.append([ncol,[points[l][b],points[l][(b+1)%len(points[1])],points[l+1][(b+1)%len(points[1])],points[l+1][b]],0,0])
    return poly

def chicken_maker():
    poly = []
    scale = 10
    search = [[1,0,0,[[1,0,0],[1,1,0],[1,1,1],[1,0,1]]],
              [-1,0,0,[[0,0,0],[0,0,1],[0,1,1],[0,1,0]]],
              [0,1,0,[[0,1,0],[0,1,1],[1,1,1],[1,1,0]]],
              [0,-1,0,[[0,0,0],[1,0,0],[1,0,1],[0,0,1]]],
              [0,0,1,[[0,0,1],[1,0,1],[1,1,1],[0,1,1]]],
              [0,0,-1,[[0,0,0],[0,1,0],[1,1,0],[1,0,0]]]]
    
    key = {1:(255,255,255),2:(255,93,147),3:(0,0,0),4:(255,128,103)}
    layout=[[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,2,2,2,2,0,0,0,0,0],
            [0,0,0,0,0,0,2,2,2,2,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
           [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,2,2,2,2,0,0,0,0,0],
            [0,0,0,0,0,0,2,2,2,2,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
           [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
           [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
           [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,1,1,3,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [4,4,4,1,1,1,1,1,1,1,1,0,0,0,0],
            [4,4,4,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,3,1,1,1,1,1,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
           [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [4,4,4,1,1,1,1,1,1,1,1,0,0,0,0],
            [4,4,4,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
           [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,2,2,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,2,2,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
           [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,2,2,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,2,2,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
           [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
           [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
           [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
           [[0,0,0,0,0,1,1,1,1,1,1,1,0,0,0],
            [0,0,0,0,0,1,1,1,1,1,1,1,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,0,0,0,0,1,1,1,1,1,1,1,0,0,0],
            [0,0,0,0,0,1,1,1,1,1,1,1,0,0,0]],
           [[0,0,0,0,0,1,1,1,1,1,1,1,0,0,0],
            [0,0,0,0,0,1,1,1,1,1,1,1,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,0,0,0,0,1,1,1,1,1,1,1,0,0,0],
            [0,0,0,0,0,1,1,1,1,1,1,1,0,0,0]],
           [[0,0,0,0,0,1,1,1,1,1,1,1,0,0,0],
            [0,0,0,0,0,1,1,1,1,1,1,1,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,0,0,0,0,1,1,1,1,1,1,1,0,0,0],
            [0,0,0,0,0,1,1,1,1,1,1,1,0,0,0]],
           [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
           [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,4,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,4,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
           [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,4,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,4,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
           [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,4,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,4,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
           [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,4,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,4,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
           [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,4,4,4,4,4,0,0,0,0,0,0],
            [0,0,0,0,0,0,4,4,4,0,0,0,0,0,0],
            [0,0,0,0,4,4,4,4,4,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,4,4,4,4,4,0,0,0,0,0,0],
            [0,0,0,0,0,0,4,4,4,0,0,0,0,0,0],
            [0,0,0,0,4,4,4,4,4,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]]
       
    for y in range(len(layout)):
        for x in range(len(layout[y])):
            for z in range(len(layout[y][x])):
                if layout[y][x][z]!=0:
                    for s in search:
                        make = False
                        if y+s[0]>0 and y+s[0]<len(layout) and x+s[1]>0 and x+s[1]<len(layout[y]) and z+s[2]>0 and z+s[2]<len(layout[y][x]):
                            if layout[y+s[0]][x+s[1]][z+s[2]] == 0:
                                make = True
                        else: make = True
                        if make:
                            if layout[y][x][z]==1:
                                c = random.randint(247,255)
                                ncol = [c,c,c]
                            else: ncol = key[layout[y][x][z]][:]
                            poly.append([ncol,[[(s[3][0][1]+x)*scale,(s[3][0][0]+y)*scale,(s[3][0][2]+z)*scale],
                                               [(s[3][1][1]+x)*scale,(s[3][1][0]+y)*scale,(s[3][1][2]+z)*scale],
                                               [(s[3][2][1]+x)*scale,(s[3][2][0]+y)*scale,(s[3][2][2]+z)*scale],
                                               [(s[3][3][1]+x)*scale,(s[3][3][0]+y)*scale,(s[3][3][2]+z)*scale]]])
    return poly

def lightcalc(poly,l):
    v1 = [poly[1][0]-poly[0][0],poly[1][1]-poly[0][1],poly[1][2]-poly[0][2]]
    v2 = [poly[2][0]-poly[0][0],poly[2][1]-poly[0][1],poly[2][2]-poly[0][2]]
    n = [v1[1]*v2[2]-v1[2]*v2[1],
              v1[2]*v2[0]-v1[0]*v2[2],
              v1[0]*v2[1]-v1[1]*v2[0]]

    try:
        costheta = (n[0]*l[0]+n[1]*l[1]+n[2]*l[2])/(pythag3d([0,0,0],n)*pythag3d([0,0,0],l))
    except:
        costheta = 1

    return (costheta+1)/2

def polyprocess(poly,light):
    npoly = []
    for a in poly:
        if len(a[1]) == 3:
            npoly.append([a[0],a[1],0])
        elif len(a[1]) == 4:
            temp = copy.deepcopy(a[1])
            del temp[3]
            npoly.append([a[0],temp,0])
            temp2 = copy.deepcopy(a[1])
            del temp2[1]
            npoly.append([a[0],temp2,0])
        else:
            print(len(a[1]),a)
    for a in range(len(npoly)):
        npoly[a].append(avpoint(npoly[a][1]))
        npoly[a].append(lightcalc(npoly[a][1],light))
    return npoly
    

#x,y,z, xr,yr,zr
camera = [0,0,-200.0001,0,0,0]
focallength = 1000
FOV = 45
drawingmode = False
drawingcol = [0,100,255]
drawingcursordata = [0,0]
drawingdown = False

##poly = [[(255,0,0),[(-1000,0,0),(1000,0,0)],0],
##        [(0,255,0),[(0,-1000,0),(0,1000,0)],0],
##        [(0,0,255),[(0,0,-1000),(0,0,1000)],0],
##poly = [[(185,0,0),[(-100,-100,-100),(100,-100,-100),(100,100,-100),(-100,100,-100)],0],
##        [(255,89,0),[(-100,-100,100),(100,-100,100),(100,100,100),(-100,100,100)],0],
##        [(255,213,0),[(-100,-100,-100),(-100,-100,100),(100,-100,100),(100,-100,-100)],0],
##        [(0,69,173),[(100,-100,-100),(100,-100,100),(100,100,100),(100,100,-100)],0],
##        [(255,255,255),[(100,100,-100),(100,100,100),(-100,100,100),(-100,100,-100)],0],
##        [(0,155,72),[(-100,100,-100),(-100,100,100),(-100,-100,100),(-100,-100,-100)],0],
##        ]
poly = donut_maker(100,70,300,100,0,30,(0,0,0))
poly+= chicken_maker()

lightvector = [20,10,30]
poly = polyprocess(poly,lightvector)



cursormove = [0,0]
pygame.mouse.set_pos((screenw/2,screenh/2))
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
            if event.key == pygame.K_F5:
                if drawingmode:
                    pygame.mouse.set_visible(False)
                    drawingmode = False
                else:
                    pygame.mouse.set_visible(True)
                    drawingcursordata = list(pygame.mouse.get_pos())
                    drawingmode = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4: FOV-=3
            elif event.button == 5: FOV+=3
            if FOV<5: FOV = 5
            elif FOV>81: FOV = 81
            focallength = (screenw/2)/math.tan(FOV*math.pi/180)
    cursormove = pygame.mouse.get_rel()
    if not drawingmode:
        pygame.mouse.set_pos((screenw/2,screenh/2))
        screen.fill((150,150,150))
        camera = controller(camera,cursormove)
        polydrawer(poly,camera,focallength,screen)
        pygame.display.flip()
    else:
        mprs = pygame.mouse.get_pressed()
        mpos = pygame.mouse.get_pos()
        pygame.draw.rect(screen,drawingcol,pygame.Rect(screenw-60,10,50,50))
        if mprs[1]:
            if not drawingdown:
                poly.append([drawingcol[:],[],0])
            drawingdown = True
            cursormove = list(pygame.mouse.get_pos())
            cursormove[0]-=drawingcursordata[0]
            cursormove[1]-=drawingcursordata[1]
            cursormove[0]*=-1
            cursormove[1]*=-1
            drawing(mpos,camera,focallength,poly)
        else:
            drawingdown = False
            cursormove = [0,0]
        drawingcursordata = list(pygame.mouse.get_pos())
        screen.fill((150,150,150))
        camera = controller(camera,cursormove)
        polydrawer(poly,camera,focallength,screen)
        pygame.display.flip()
            
        
    clock.tick(60)
pygame.quit()
        
