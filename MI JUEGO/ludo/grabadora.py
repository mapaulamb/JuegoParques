import pickle
from ludo.juego import Jugador


class RegistroDeJuego():
    '''Proporciona los datos grabados del juego
    Iterando sobre la instancia
    Devuelve el valor del dado y el índice
    '''

    def __init__(self, archivo_obj):
        self.archivo_obj = archivo_obj
        datos = pickle.load(self.archivo_obj)
        self.jugadores = datos[0]
        self.historial_del_juego = datos[1]

    def obtener_jugadores(self, func=None):
        '''
        Devuelve el objeto Player
        recreado desde una lista
        func es una función callable que el jugador
        podría necesitar para delegación de elecciones
        '''
        res = []
        for color, nombre, es_computadora in self.jugadores:
            if es_computadora:
                jugador = Jugador(color)
            else:
                jugador = Jugador(color, nombre, func)
            res.append(jugador)
        return res

    def obtener_historial_del_juego(self):
        return self.historial_del_juego

    def __iter__(self):
        return iter(self.historial_del_juego)


class CrearRegistro():
    '''Guarda los datos del juego
    como una lista anidada que es
    guardada con pickle
    '''

    def __init__(self):
        self.jugadores = []
        self.historial_del_juego = []

    def agregar_jugador(self, objeto_jugador):
        '''Acepta el objeto Player y
        lo guarda NO como objeto, sino como una lista
        '''
        if objeto_jugador.elegir_ficha_delegate is None:
            es_computadora = True
        else:
            es_computadora = False
        self.jugadores.append((objeto_jugador.color,
                               objeto_jugador.nombre, es_computadora))

    def agregar_turno_del_juego(self, valor_roll, indice):
        self.historial_del_juego.append((valor_roll, indice))

    def guardar(self, archivo_obj):
        '''Lista de listas con los jugadores y
        el historial del juego
        '''
        pickle.dump([self.jugadores, self.historial_del_juego],
                    archivo_obj)
