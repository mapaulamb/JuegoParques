# Importamos las clases y funciones necesarias de otros módulos del juego
from ludo.juego import Jugador, Juego
from ludo.pintor import mostrar_dado_con_jugador
from ludo.grabadora import RegistroDeJuego, CrearRegistro
from os import linesep

class JuegoCLI():
    """
    Clase que maneja la interfaz de línea de comandos para el juego de parqués.
    Permite iniciar una nueva partida, continuar una partida guardada o ver una partida grabada.
    """

    def __init__(self):
        self.prompt_end = "> "  # Símbolo para indicar entrada del usuario
        self.juego = Juego()  # Inicializa el juego
        self.seleccion_ficha = False  # Para mejorar la presentación del texto
        self.creador_registro = CrearRegistro()  # Para guardar los datos del juego
        self.ejecutor_registro = None  # Para recuperar datos de un juego guardado

    def validar_entrada(self, mensaje, tipo_dato, opciones_permitidas=None,
                        mensaje_error="¡Opción no válida!", longitud_str=None):
        """
        Solicita una entrada del usuario y la valida.
        - `opciones_permitidas`: Lista de valores permitidos.
        - `longitud_str`: Tupla con el mínimo y máximo de caracteres permitidos si es una cadena.
        """
        mensaje += linesep + self.prompt_end
        while True:
            entrada = input(mensaje)
            if not entrada:
                print(linesep + mensaje_error)
                continue
            try:
                entrada = tipo_dato(entrada)
            except ValueError:
                print(linesep + mensaje_error)
                continue
            if opciones_permitidas:
                if entrada in opciones_permitidas:
                    break
                else:
                    print("¡Opción no válida!")
                    continue
            elif longitud_str:
                min_len, max_len = longitud_str
                if min_len < len(entrada) < max_len:
                    break
                else:
                    print(linesep + mensaje_error)
            else:
                break
        print()
        return entrada

    def obtener_opcion_inicial(self):
        """Muestra el menú inicial y obtiene la opción del usuario."""
        opciones = linesep.join([
            "Seleccione una opción:",
            "0 - Iniciar nueva partida",
            "1 - Continuar partida guardada",
            "2 - Ver una partida grabada"
        ])
        return self.validar_entrada(opciones, int, (0, 1, 2))

    def solicitar_archivo(self, modo="rb"):
        """Solicita al usuario el nombre del archivo de registro y lo abre."""
        mensaje = "Ingrese el nombre del archivo de registro:"
        while True:
            nombre_archivo = self.validar_entrada(mensaje, str)
            try:
                archivo = open(nombre_archivo, mode=modo)
                return archivo
            except IOError as e:
                print(e)
                print("Intente nuevamente.")

    def desea_guardar_partida(self):
        """Pregunta al usuario si desea guardar la partida actual."""
        opciones = linesep.join([
            "¿Desea guardar la partida?",
            "0 - No",
            "1 - Sí"
        ])
        return self.validar_entrada(opciones, int, (0, 1)) == 1

    def solicitar_jugador(self):
        """Solicita los datos del jugador y lo agrega al juego."""
        colores_disponibles = self.juego.obtener_colores_disponibles()
        opciones_tipo_jugador = linesep.join([
            "Seleccione el tipo de jugador:",
            "0 - Computadora",
            "1 - Humano"
        ])
        tipo_jugador = self.validar_entrada(opciones_tipo_jugador, int, (0, 1))

        if tipo_jugador == 1:
            nombre = self.validar_entrada("Ingrese el nombre del jugador:", str, longitud_str=(1, 30))
            opciones_colores = range(len(colores_disponibles))
            if len(opciones_colores) > 1:
                opciones = ["{} - {}".format(i, color) for i, color in enumerate(colores_disponibles)]
                seleccion_color = self.validar_entrada("Seleccione un color:" + linesep + linesep.join(opciones), int, opciones_colores)
                color = colores_disponibles.pop(seleccion_color)
            else:
                color = colores_disponibles.pop()
            jugador = Jugador(color, nombre, self.solicitar_ficha)
        else:
            color = colores_disponibles.pop()
            jugador = Jugador(color)

        self.juego.agregar_jugador(jugador)

    def solicitar_jugadores(self):
        """Agrega jugadores a la partida, permitiendo un mínimo de 2 y un máximo de 4."""
        for i in range(2):
            print(f"Agregando el jugador {i + 1}...")
            self.solicitar_jugador()
            print("Jugador agregado.")

        for i in range(2, 4):
            opciones = linesep.join([
                "Seleccione una opción:",
                f"0 - Agregar otro jugador",
                f"1 - Iniciar partida con {i} jugadores"
            ])
            eleccion = self.validar_entrada(opciones, int, (0, 1))
            if eleccion == 1:
                break
            elif eleccion == 0:
                print(f"Agregando el jugador {i + 1}...")
                self.solicitar_jugador()
                print("Jugador agregado.")

    def solicitar_ficha(self):
        """Pregunta al usuario qué peón desea mover cuando tiene más de una opción."""
        mensaje = mostrar_dado_con_jugador(self.juego.valor_dado, str(self.juego.jugador_actual))
        mensaje += linesep + "Tiene más de un peón que puede mover. Seleccione uno:" + linesep
        opciones_fichas = ["{} - {}".format(i + 1, ficha.id) for i, ficha in enumerate(self.juego.fichas_movibles)]
        mensaje += linesep.join(opciones_fichas)
        indice = self.validar_entrada(mensaje, int, range(1, len(self.juego.fichas_movibles) + 1))
        self.seleccion_ficha = True
        return indice - 1
    
    def solicitar_continuar(self):
        texto = "Presiona Enter para continuar" + linesep
        input(texto)

    def imprimir_info_jugadores(self):
        palabra = "iniciar" if self.juego.valor_dado is None else "continuar"
        print("Juego {} con {} jugadores:".format(
              palabra,
              len(self.juego.jugadores)))
        for jugador in self.juego.jugadores:
            print(jugador)
        print()

    def imprimir_info_despues_turno(self):
        '''Utiliza atributos del juego para imprimir información'''
        ids_fichas = [ficha.id for ficha in self.juego.fichas_movibles]
        # Mejor presentación del dado
        mensaje = mostrar_dado_con_jugador(self.juego.valor_dado,
                                          str(self.juego.jugador_actual))
        mensaje += linesep
        if self.juego.fichas_movibles:
            mensaje_movido = "{} ha sido movida. ".format(
                self.juego.ficha_elegida.id)
            if self.seleccion_ficha:
                self.seleccion_ficha = False
                print(mensaje_movido)
                return
            mensaje += "{} fichas posibles para mover.".format(
                " ".join(ids_fichas))
            mensaje += " " + mensaje_movido
            if self.juego.fichas_expulsadas:
                mensaje += "Ficha en carrera "
                mensaje += " ".join([ficha.id for ficha in self.juego.fichas_expulsadas])
        else:
            mensaje += "No hay fichas posibles para mover."
        print(mensaje)

    def imprimir_clasificacion(self):
        lista_clasificacion = ["{} - {}".format(indice + 1, jugador)
                               for indice, jugador in enumerate(self.juego.clasificacion)]
        mensaje = "Clasificación:" + linesep + linesep.join(lista_clasificacion)
        print(mensaje)

    def imprimir_tablero(self):
        print(self.juego.obtener_imagen_tablero())

    def ejecutar_juego_grabado(self):
        '''Obtiene el historial del juego (valor del dado
        y el índice de la ficha permitida) de 
        record_runner para reproducir el juego'''
        self.cargar_jugadores_grabados()
        self.imprimir_info_jugadores()
        self.solicitar_continuar()
        for valor_dado, indice in self.ejecutor_registro:
            self.juego.jugar_turno(indice, valor_dado)
            self.imprimir_info_despues_turno()
            self.imprimir_tablero()
            self.solicitar_continuar()
            self.imprimir_tablero()

    def continuar_juego_grabado(self):
        '''Avanza el juego llamando 
        al método jugar_turno hasta el punto 
        donde fue interrumpido.'''
        self.cargar_jugadores_grabados()
        self.grabar_jugadores()
        for valor_dado, indice in self.ejecutor_registro:
            self.juego.jugar_turno(indice, valor_dado)
            self.creador_registro.agregar_turno_del_juego(
                self.juego.valor_dado, self.juego.indice)
        self.imprimir_info_jugadores()
        self.imprimir_info_despues_turno()
        self.imprimir_tablero()

    def grabar_jugadores(self):
        '''Guarda los jugadores en el registrador'''
        for jugador in self.juego.jugadores:
            self.creador_registro.agregar_jugador(jugador)

    def cargar_jugadores_grabados(self):
        '''Obtiene los jugadores guardados en el registrador
        y los añade al juego'''
        if self.ejecutor_registro is None:
            archivo = self.solicitar_archivo()
            self.ejecutor_registro = RegistroDeJuego(archivo)
            archivo.close()
        for jugador in self.ejecutor_registro.obtener_jugadores(
                self.solicitar_ficha):
            self.juego.agregar_jugador(jugador)

    def cargar_jugadores_nuevo_juego(self):
        self.solicitar_jugadores()
        self.imprimir_info_jugadores()
        self.grabar_jugadores()

    def jugar(self):
        '''Llama principalmente al método jugar_turno
        del juego mientras no haya terminado'''
        try:
            while not self.juego.finalizado:
                self.juego.jugar_turno()
                self.imprimir_info_despues_turno()
                self.imprimir_tablero()
                self.creador_registro.agregar_turno_del_juego(
                    self.juego.valor_dado, self.juego.indice)
                self.solicitar_continuar()
            print("Juego terminado")
            self.imprimir_clasificacion()
            self.ofrecer_guardar_juego()
        except (KeyboardInterrupt, EOFError):
            print(linesep +
                  "Saliendo del juego. " +
                  "¿Guardar y continuar más tarde?")
            self.ofrecer_guardar_juego()
            raise

    def ofrecer_guardar_juego(self):
        '''Ofrece al usuario guardar el juego'''
        if self.desea_guardar_partida():
            archivo = self.solicitar_archivo(modo="wb")
            self.creador_registro.guardar(archivo)
            archivo.close()
            print("Juego guardado")

    def iniciar(self):
        '''Método principal, inicia la interfaz de línea de comandos'''
        print()
        try:
            opcion = self.obtener_opcion_inicial()
            if opcion == 0:  # Iniciar nuevo juego
                self.cargar_jugadores_nuevo_juego()
                self.jugar()
            elif opcion == 1:  # Continuar juego guardado
                self.continuar_juego_grabado()
                if self.juego.terminado:
                    print("No se pudo continuar.",
                          "El juego ya ha finalizado",
                          linesep + "Saliendo")
                else:
                    self.solicitar_continuar()
                    self.jugar()
            elif opcion == 2:  # Revisar partida jugada
                self.ejecutar_juego_grabado()
        except (KeyboardInterrupt, EOFError):
            print(linesep + "Saliendo del juego.")


if __name__ == '__main__':
    JuegoCLI().iniciar()

    