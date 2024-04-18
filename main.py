import pygame
from pygame.locals import *
import random

pygame.init()

#TIMER
clock = pygame.time.Clock()
fps = 60

#TELA
largura = 860
altura = 930
tela = pygame.display.set_mode((largura, altura))

#LEGENDA
pygame.display.set_caption('Flappy Bird')

#FONTE
fonte = pygame.font.SysFont('Bauhaus 93', 60)

#CORES
branco = (255, 255, 255)

#VARIAVEIS
terra_scroll = 0
veloc_scroll = 4
voando = False
fim = False
pipe_gap = 150
frequencia_pipe = 1500 #milisegundos
ultimo_pipe = pygame.time.get_ticks() - frequencia_pipe
pontuacao = 0
pipe_passar = False

#IMAGENS
bg = pygame.image.load('img/bg.png')
chao = pygame.image.load('img/ground.png')
botao_img = pygame.image.load('img/restart.png')

#TEXTO
def desenhar_texto(texto, fonte, cor_texto, x, y):
    img = fonte.render(texto, True, cor_texto)
    tela.blit(img, (x, y))

def reset():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(altura / 2)
    pontuacao = 0
    return pontuacao

#CLASSE BIRD
class Bird(pygame.sprite.Sprite):
    
    #PERMITE QUE O PYGAME NAO PRECISE USAR OUTROS COMANDOS, COMO BLIT
    def __init__ (self, x, y):
        pygame.sprite.Sprite.__init__(self)

        #LISTA VAZIA
        self.images = []
        self.index = 0
        self.counter = 0

        for num in range(1,4):
            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        #VELOCIDADE
        self.vel = 0
        self.clicar = False


    def update(self):
        global ultimo_pipe
        if voando == True:
            #GRAVIDADE
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 760:
                self.rect.y += int(self.vel)

        if fim == False:

            #GERAR NOVOS PIPES
            time_now = pygame.time.get_ticks()
            if time_now - ultimo_pipe > frequencia_pipe:
                pipe_de_baixo = Pipe(largura, int(altura / 2), -1)
                pipe_de_cima = Pipe(largura, int(altura / 2), 1)
                pipe_group.add(pipe_de_baixo)
                pipe_group.add(pipe_de_cima)

                ultimo_pipe = time_now

            #PULAR NO CLIQUE ESQUERDO DO MOUSE
            if pygame.mouse.get_pressed()[0] == 1 and self.clicar == False:
                self.clicar = True
                self.veloc = -10

            if pygame.mouse.get_pressed()[0] == 0:
                self.clicar = False

            self.counter += 1
            cooldown = 5
            if self.counter > cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            #ROTACIONAR PARA CIMA E PARA BAIXO | -2 PARA GIRAR NO SENTIDO HORARIO
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        #FICA EM 90 GRAUS
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()

        #POSICAO 1: EM CIMA; POSICAO -1: EMBAIXO
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= veloc_scroll
        if self.rect.right < 0:
            self.kill()
    
class Botao():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):

        acao = False

        #POSICAO DO MOUSE
        pos = pygame.mouse.get_pos()

        #CHECAR SE O MOUSE ESTA SOB O BOTAO
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                acao = True

        #DESENHAR BOTAO
        tela.blit(self.image, (self.rect.x, self.rect.y))

        return acao

bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()


flappy = Bird(100, int(altura / 2))
bird_group.add(flappy)

#BOTAO DE RESTART

botao = Botao(largura // 2 - 50, altura // 2 - 100, botao_img)

run = True
while run:
    clock.tick(fps)

    #CÉU
    tela.blit(bg, (0,0))

    #DESENHAR O BIRD
    bird_group.draw(tela)
    bird_group.update()

    #DESENHAR O PIPE
    pipe_group.draw(tela)

    #DESENHAR O CHAO
    tela.blit(chao, (terra_scroll, 760))

    #VERIFICAR A PONTUACAO
    if len(pipe_group) > 0:
        #0 POIS SO TEM UM PASSARO
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
        and bird_group.sprites()[0].rect.right > pipe_group.sprites()[0].rect.right \
        and pipe_passar == False:
            pipe_passar = True
        if pipe_passar == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                pontuacao += 1
                pipe_passar = False

    desenhar_texto(str(pontuacao), fonte, branco, int(largura / 2), 20)

    #COLISAO | SE FOR TRUE DELETA ALGUM DOS OBJETOS
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        fim = True

    
    #VERIFICAR SE O BIRD ENCOSTOU NO CHAO
    if flappy.rect.bottom >= 760:
        fim = True
        voando = False

    if fim == False and voando == True:

        #GERACAO DE NOVOS PIPES
        time_now = pygame.time.get_ticks()
        if time_now - ultimo_pipe > frequencia_pipe:
            pipe_altura = random.randint(-100, 100)
            pipe_de_baixo = Pipe(largura, int(altura / 2) + pipe_altura , -1)
            pipe_de_cima = Pipe(largura, int(altura / 2) + pipe_altura , 1)

            pipe_group.add(pipe_de_baixo)
            pipe_group.add(pipe_de_cima)

        #CHAO
        terra_scroll -= veloc_scroll
        if abs(terra_scroll) > 35:
            terra_scroll = 0

        pipe_group.update()

    #CHECAR FIM DO JOGO E REINICIAR
    if fim == True:
        if botao.draw() == True:
            fim = False
            pontuacao = reset()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and voando == False and fim == False:
            voando = True

    #ATUALIZAR O JOGO  
    pygame.display.update()
pygame.quit 