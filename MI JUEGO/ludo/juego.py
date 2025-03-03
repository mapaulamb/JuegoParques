from collections import namedtuple, deque
import random
from ludo.pintor import PintarTablero

Ficha = namedtuple("Ficha", "indice color id")


class Jugador():
    '''Almacena sus fichas, conoce su color 
    y elige qué ficha mover si hay más de una opción disponible.'''
    
    def __init__(self, color, nombre=None, elegir_ficha_delegate=None):
        '''elegir_ficha_delegate es una función invocable.
        Si elegir_ficha_delegate no es None, se llama con una lista de fichas disponibles para mover
        y se espera que devuelva el índice elegido.
        Si es None (es decir, es una computadora), se elige un índice aleatorio.
        '''
        self.color = color
        self.elegir_ficha_delegate = elegir_ficha_delegate
        self.nombre = nombre
        if self.nombre is None and self.elegir_ficha_delegate is None:
            self.nombre = "computadora"
        self.terminado = False
        # Inicializa cuatro fichas con un ID basado en la primera letra del color y un número del 1 al 4.
        self.fichas = [Ficha(i, color, color[0].upper() + str(i))
                       for i in range(1, 5)]

    def __str__(self):
        return "{}({})".format(self.nombre, self.color)

    def elegir_ficha(self, fichas):
        '''Delegar la elección de la ficha a elegir_ficha_delegate
        si no es None.
        '''
        if len(fichas) == 1:
            indice = 0
        elif len(fichas) > 1:
            if self.elegir_ficha_delegate is None:
                indice = random.randint(0, len(fichas) - 1)
            else:
                indice = self.elegir_ficha_delegate()
        return indice


class Tablero():
    '''
    Conoce la ubicación de las fichas.
    Las fichas están asignadas a números de posición.
    Puede mover (cambiar la posición) de una ficha.
    También sabe otras cosas, como la distancia que 
    una ficha debe recorrer para llegar al final.
    Es solo un tablero. No conoce las reglas del juego.
    '''

    # Casillas comunes para todas las fichas
    TAMANO_TABLERO = 56

    # Casillas seguras (privadas) para cada color
    # Son las casillas justo antes de que la ficha termine
    TAMANO_COLOR_TABLERO = 7

    ORDEN_COLORES = ['yellow', 'blue', 'red', 'green']

    # Distancia entre colores vecinos
    # (La distancia desde la casilla de inicio de un color hasta la del siguiente)
    DISTANCIA_COLORES = 14

    def __init__(self):
        # Definir la posición de inicio para cada color
        Tablero.INICIO_COLORES = {
            color: 1 + indice * Tablero.DISTANCIA_COLORES
            for indice, color in enumerate(Tablero.ORDEN_COLORES)}
        # Definir la posición final para cada color
        Tablero.FIN_COLORES = {
            color: indice * Tablero.DISTANCIA_COLORES
            for indice, color in enumerate(Tablero.ORDEN_COLORES)}
        Tablero.FIN_COLORES['yellow'] = Tablero.TAMANO_TABLERO

        # Diccionario donde la clave es la ficha y el valor es una tupla con la posición
        self.posiciones_fichas = {}

        # Pintor para representar visualmente el tablero y las posiciones de las fichas
        self.pintor = PintarTablero()

        # Posición de las fichas en la "piscina" (antes de empezar)
        self.posicion_piscina = (0, 0)

    def colocar_ficha(self, ficha, posicion):
        '''Guarda la posición de una ficha'''
        self.posiciones_fichas[ficha] = posicion

    def poner_ficha_en_piscina(self, ficha):
        self.colocar_ficha(ficha, self.posicion_piscina)

    def ficha_en_piscina(self, ficha):
        '''Devuelve True si la ficha está en la piscina, False en caso contrario.'''
        return self.posiciones_fichas[ficha] == self.posicion_piscina

    def poner_ficha_en_inicio(self, ficha):
        inicio = Tablero.INICIO_COLORES[ficha.color.lower()]
        posicion = (inicio, 0)
        self.colocar_ficha(ficha, posicion)

    def puede_mover_ficha(self, ficha, valor_dado):
        '''Verifica si la ficha puede moverse sin salirse de su zona de color.'''
        posicion_comun, posicion_privada = self.posiciones_fichas[ficha]
        return posicion_privada + valor_dado <= self.TAMANO_COLOR_TABLERO

    def mover_ficha(self, ficha, valor_dado):
        '''Cambia la posición de la ficha y verifica si ha llegado a su zona de color.'''
        posicion_comun, posicion_privada = self.posiciones_fichas[ficha]
        fin = self.FIN_COLORES[ficha.color.lower()]
        if posicion_privada > 0:
            posicion_privada += valor_dado
        elif posicion_comun <= fin and posicion_comun + valor_dado > fin:
            posicion_privada += valor_dado - (fin - posicion_comun)
            posicion_comun = fin
        else:
            posicion_comun += valor_dado
            if posicion_comun > self.TAMANO_TABLERO:
                posicion_comun -= self.TAMANO_TABLERO
        self.colocar_ficha(ficha, (posicion_comun, posicion_privada))

    def ficha_llego_al_final(self, ficha):
        '''Devuelve True si la ficha ha alcanzado el final.'''
        _, posicion_privada = self.posiciones_fichas[ficha]
        return posicion_privada == self.TAMANO_COLOR_TABLERO

    def obtener_fichas_misma_posicion(self, ficha):
        '''Devuelve una lista de fichas en la misma posición.'''
        posicion = self.posiciones_fichas[ficha]
        return [f for f, p in self.posiciones_fichas.items() if p == posicion]

    def pintar_tablero(self):
        '''Genera la representación visual del tablero.'''
        posiciones = {}
        for ficha, posicion in self.posiciones_fichas.items():
            comun, privada = posicion
            if privada != Tablero.TAMANO_COLOR_TABLERO:
                posiciones.setdefault(posicion, []).append(ficha)
        return self.pintor.pintar(posiciones)


class Dado():
    MIN = 1
    MAX = 6

    @staticmethod
    def lanzar():
        return random.randint(Dado.MIN, Dado.MAX)


class Juego():
    '''Conoce las reglas del juego.
    Gestiona eventos como cuando una ficha alcanza a otra,
    cuando una ficha llega al final, o cuando un jugador saca un seis.
    '''

    def __init__(self):
        self.jugadores = deque()
        self.clasificacion = []
        self.tablero = Tablero()
        self.finalizado = False
        self.valor_dado = None
        self.jugador_actual = None
        self.fichas_movibles = []
        self.ficha_elegida = None
        self.indice = None
        self.fichas_expulsadas = []

    def agregar_jugador(self, jugador):
        self.jugadores.append(jugador)
        for ficha in jugador.fichas:
            self.tablero.poner_ficha_en_piscina(ficha)

    def obtener_colores_disponibles(self):
        '''Devuelve los colores aún disponibles en el tablero.'''
        usados = [jugador.color for jugador in self.jugadores]
        return sorted(set(self.tablero.ORDEN_COLORES) - set(usados))

    def turno_siguiente(self):
        '''Determina el siguiente jugador en turno.'''
        if self.valor_dado != Dado.MAX:
            self.jugadores.rotate(-1)
        return self.jugadores[0]
    def obtener_ficha_de_la_piscina(self, jugador):
        '''Obtiene una ficha de la piscina del tablero cuando debe comenzar.'''
        for ficha in jugador.fichas:
            if self.tablero.ficha_en_piscina(ficha):
                return ficha

    def obtener_fichas_permitidas_para_mover(self, jugador, valor_dado):
        ''' Devuelve todas las fichas de un jugador que pueden moverse 
        con el valor obtenido en el dado.'''
        fichas_movibles = []
        if valor_dado == Dado.MAX:  # Si se obtiene el valor máximo en el dado
            ficha = self.obtener_ficha_de_la_piscina(jugador)
            if ficha:
                fichas_movibles.append(ficha)
        for ficha in jugador.fichas:
            # Verifica si la ficha no está en la piscina y si puede moverse
            if not self.tablero.ficha_en_piscina(ficha) and \
                    self.tablero.puede_mover_ficha(ficha, valor_dado):
                fichas_movibles.append(ficha)
        # Ordena las fichas permitidas según su índice
        return sorted(fichas_movibles, key=lambda ficha: ficha.indice)

    def obtener_imagen_tablero(self):
        '''Devuelve una representación visual del tablero.'''
        return self.tablero.pintar_tablero()

    def empujar_ficha_extranjera(self, ficha):
        '''Si hay fichas de otro color en la misma posición, las envía a la piscina.'''
        fichas = self.tablero.obtener_fichas_misma_posicion(ficha)
        for f in fichas:
            if f.color != ficha.color:  # Solo afecta a fichas de otro color
                self.tablero.poner_ficha_en_piscina(f)
                self.fichas_expulsadas.append(f)

    def realizar_movimiento(self, jugador, ficha):
        '''Mueve una ficha en el tablero. Luego verifica si la ficha llegó al final
        o si debe empujar a otras fichas. También comprueba si el jugador ha terminado.'''
        
        # Si el dado sacó el valor máximo y la ficha está en la piscina, la mueve a la casilla inicial
        if self.valor_dado == Dado.MAX and \
                self.tablero.ficha_en_piscina(ficha):
            self.tablero.poner_ficha_en_inicio(ficha)
            self.empujar_ficha_extranjera(ficha)
            return

        # Mueve la ficha en el tablero
        self.tablero.mover_ficha(ficha, self.valor_dado)

        # Verifica si la ficha ha llegado al final
        if self.tablero.ficha_llego_al_final(ficha):
            jugador.fichas.remove(ficha)  # Elimina la ficha de la lista del jugador
            if not jugador.fichas:  # Si ya no quedan fichas, el jugador ha terminado
                self.clasificacion.append(jugador)
                self.jugadores.remove(jugador)
                if len(self.jugadores) == 1:
                    self.clasificacion.extend(self.jugadores)
                    self.terminado = True
        else:
            self.empujar_ficha_extranjera(ficha)  # Verifica si debe empujar fichas rivales

    def jugar_turno(self, indice=None, valor_dado=None):
        '''Método principal para jugar un turno.
        Selecciona al siguiente jugador, lanza el dado, elige una ficha y la mueve.
        Los parámetros "indice" y "valor_dado" se usan cuando se quiere reproducir un juego guardado.
        '''
        
        self.fichas_expulsadas = []
        self.jugador_actual = self.turno_siguiente()

        # Lanza el dado si no se proporcionó un valor específico
        if valor_dado is None:
            self.valor_dado = Dado.lanzar()
        else:
            self.valor_dado = valor_dado

        # Obtiene las fichas que pueden moverse con el valor obtenido en el dado
        self.fichas_movibles = self.obtener_fichas_permitidas_para_mover(
            self.jugador_actual, self.valor_dado)

        if self.fichas_movibles:
            # Si no se proporciona un índice, el jugador elige una ficha
            if indice is None:
                self.indice = self.jugador_actual.elegir_ficha(self.fichas_movibles)
            else:
                self.indice = indice
            
            # Selecciona la ficha y la mueve
            self.ficha_elegida = self.fichas_movibles[self.indice]
            self.realizar_movimiento(self.jugador_actual, self.ficha_elegida)
        else:
            # Si no hay fichas disponibles para mover, se registra como -1
            self.indice = -1
            self.ficha_elegida = None

    