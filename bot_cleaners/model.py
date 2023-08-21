from mesa.model import Model
from mesa.agent import Agent
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
from math import sqrt

import numpy as np


class Cargador(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class Celda(Agent):
    def __init__(self, unique_id, model, suciedad: bool = False):
        super().__init__(unique_id, model)
        self.sucia = suciedad

class Mueble(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class RobotLimpieza(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.movimientos = 0
        self.carga = 100
        self.cargando = False

    def limpiar_una_celda(self, lista_de_celdas_sucias):
        celda_a_limpiar = self.random.choice(lista_de_celdas_sucias)
        celda_a_limpiar.sucia = False
        self.sig_pos = celda_a_limpiar.pos

    def seleccionar_nueva_pos(self, lista_de_vecinos):
        self.sig_pos = self.random.choice(lista_de_vecinos).pos

    def buscar_cargador(self, cargadores):
        distancias = []
        for i in cargadores:
            # Calula la distancia entre el robot y los cargadores
            xi, yi = self.pos
            xf, yf = i.pos
            dist = sqrt((xf - xi) ** 2 + (yf - yi) ** 2)
            distancias.append(dist)
        # Obtiene el cargador mas cercano
        cargador_cercano = cargadores[distancias.index(min(distancias))]
        return cargador_cercano

    def moverse_a(self, pos):
        xf, yf = pos
        xi, yi = self.pos
        if xf > xi:
            self.sig_pos = (xi + 1, yi)
        elif xf < xi:
            self.sig_pos = (xi - 1, yi)
        elif yf > yi:
            self.sig_pos = (xi, yi + 1)
        elif yf < yi:
            self.sig_pos = (xi, yi - 1)

    @staticmethod
    def buscar_celdas_sucia(lista_de_vecinos):
        # #Opción 1
        # return [vecino for vecino in lista_de_vecinos
        #                 if isinstance(vecino, Celda) and vecino.sucia]
        # #Opción 2
        celdas_sucias = list()
        for vecino in lista_de_vecinos:
            if isinstance(vecino, Celda) and vecino.sucia:
                celdas_sucias.append(vecino)
        return celdas_sucias

    def step(self):

        if self.cargando:
            if self.carga < 100:
                self.carga += 1
            else:
                self.cargando = False
        else:
            vecinos = self.model.grid.get_neighbors(
                self.pos, moore=True, include_center=False
            )

            for vecino in vecinos:
                if isinstance(vecino, (Mueble, RobotLimpieza)):
                    vecinos.remove(vecino)

            celdas_sucias = self.buscar_celdas_sucia(vecinos)

            if len(celdas_sucias) == 0:
                compañeros = []
                for content, pos in self.model.grid.coord_iter():
                    for obj in content:
                        if isinstance(obj, RobotLimpieza) and obj.unique_id != self.unique_id:
                            compañeros.append(obj)

                for robot in compañeros:
                    vecinos_compañeros = robot.model.grid.get_neighbors(
                        robot.pos, moore=True, include_center=False
                    )
                    for vecino in vecinos_compañeros:
                        if isinstance(vecino, (Mueble, RobotLimpieza)):
                            vecinos_compañeros.remove(vecino)
                    celdas_sucias_compañeros = robot.buscar_celdas_sucia(vecinos_compañeros)
                    if len(celdas_sucias_compañeros) > 0:
                        self.moverse_a(robot.pos)
                        break
                    else:
                        self.seleccionar_nueva_pos(vecinos)
                        break
            else:
                self.limpiar_una_celda(celdas_sucias)

        if self.carga < 25:
            cargadores = [ ]
            for content, pos in self.model.grid.coord_iter():
                for obj in content:
                    if isinstance(obj, Cargador):
                        cargadores.append(obj)
            cargador = self.buscar_cargador(cargadores)
            self.moverse_a(cargador.pos)
            if self.pos == cargador.pos:
                self.cargando = True


    def advance(self):
        if self.pos != self.sig_pos:
            self.movimientos += 1

        if not self.cargando:
            if self.carga > 0:
                self.carga -= 1
                self.model.grid.move_agent(self, self.sig_pos)


class Habitacion(Model):
    def __init__(
        self,
        M: int,
        N: int,
        num_agentes: int = 5,
        porc_celdas_sucias: float = 0.6,
        porc_muebles: float = 0.1,
        modo_pos_inicial: str = "Fija",
        num_cargadores: int = 4,
    ):
        self.num_agentes = num_agentes
        self.porc_celdas_sucias = porc_celdas_sucias
        self.porc_muebles = porc_muebles
        self.num_cargadores = num_cargadores

        self.grid = MultiGrid(M, N, False)
        self.schedule = SimultaneousActivation(self)
        
        self.datacollector = DataCollector(
            model_reporters={
                "Grid": get_grid,
                "Cargas": get_cargas,
                "CeldasSucias": get_sucias,
                "TiempoLimpiezaCompleta": self.todoLimpio,
                "TotalMovimientos": get_movimientos,
                "RecargasCompletas": get_cargas,
            },
        )

        posiciones_disponibles = [pos for _, pos in self.grid.coord_iter()]

        # Posicionamiento de cargadores

        # Dividir el plano en cuatro cuadrantes
        cuadrante_1 = []
        cuadrante_2 = []
        cuadrante_3 = []
        cuadrante_4 = []
        for i in range(M):
            for j in range(N):
                if i < M / 2 and j < N / 2:
                    cuadrante_1.append((i, j))
                elif i < M / 2 and j >= N / 2:
                    cuadrante_2.append((i, j))
                elif i >= M / 2 and j < N / 2:
                    cuadrante_3.append((i, j))
                elif i >= M / 2 and j >= N / 2:
                    cuadrante_4.append((i, j))
        # Colocar un cargador en cada cuadrante
        posiciones_cargadores = []
        posiciones_cargadores.append(self.random.choice(cuadrante_1))
        posiciones_cargadores.append(self.random.choice(cuadrante_2))
        posiciones_cargadores.append(self.random.choice(cuadrante_3))
        posiciones_cargadores.append(self.random.choice(cuadrante_4))
        # Colocar los cargadores
        for id, pos in enumerate(posiciones_cargadores):
            cargador = Cargador(int(f"{num_agentes}00{id}") + 1, self)
            self.grid.place_agent(cargador, pos)
            posiciones_disponibles.remove(pos)

        # Posicionamiento de muebles
        num_muebles = int(M * N * porc_muebles)
        posiciones_muebles = self.random.sample(posiciones_disponibles, k=num_muebles)

        for id, pos in enumerate(posiciones_muebles):
            mueble = Mueble(int(f"{num_agentes}0{id}") + 1, self)
            self.grid.place_agent(mueble, pos)
            posiciones_disponibles.remove(pos)

        # Posicionamiento de celdas sucias
        self.num_celdas_sucias = int(M * N * porc_celdas_sucias)
        posiciones_celdas_sucias = self.random.sample(
            posiciones_disponibles, k=self.num_celdas_sucias
        )

        for id, pos in enumerate(posiciones_disponibles):
            suciedad = pos in posiciones_celdas_sucias
            celda = Celda(int(f"{num_agentes}{id}") + 1, self, suciedad)
            self.grid.place_agent(celda, pos)

        """
        Contar celdas sucias
        Reducir el contador con cada celda que se limpie
        Detener tiempo cuando el contador llegue a 0
        """

        # Posicionamiento de agentes robot
        if modo_pos_inicial == "Aleatoria":
            pos_inicial_robots = self.random.sample(
                posiciones_disponibles, k=num_agentes
            )
        else:  # 'Fija'
            pos_inicial_robots = [(1, 1)] * num_agentes

        for id in range(num_agentes):
            robot = RobotLimpieza(id, self)
            self.grid.place_agent(robot, pos_inicial_robots[id])
            self.schedule.add(robot)

    def get_total_movimientos(model: Model):
        return sum([agent.movimientos for agent in model.schedule.agents])

    def get_recargas_completas(model: Model):
        return sum([1 for agent in model.schedule.agents if agent.carga == 100])
    
    def step(self):
        if self.todoLimpio():
            self.running = False

        self.datacollector.collect(self)

        for agent in self.schedule.agents:
            agent.step()

        for agent in self.schedule.agents:
            agent.advance()

    def todoLimpio(self):
        for content, pos in self.grid.coord_iter():
            for obj in content:
                if isinstance(obj, Celda) and obj.sucia:
                    return False
        return True


def get_grid(model: Model) -> np.ndarray:
    """
    Método para la obtención de la grid y representarla en un notebook
    :param model: Modelo (entorno)
    :return: grid
    """
    grid = np.zeros((model.grid.width, model.grid.height))
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        x, y = pos
        for obj in cell_content:
            if isinstance(obj, RobotLimpieza):
                grid[x][y] = 2
            elif isinstance(obj, Celda):
                grid[x][y] = int(obj.sucia)
    return grid


def get_cargas(model: Model):
    return [(agent.unique_id, agent.carga) for agent in model.schedule.agents]


def get_sucias(model: Model) -> int:
    """
    Método para determinar el número total de celdas sucias
    :param model: Modelo Mesa
    :return: número de celdas sucias
    """
    sum_sucias = 0
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        for obj in cell_content:
            if isinstance(obj, Celda) and obj.sucia:
                sum_sucias += 1
    return sum_sucias / model.num_celdas_sucias


def get_movimientos(agent: Agent) -> dict:
    if isinstance(agent, RobotLimpieza):
        return {agent.unique_id: agent.movimientos}
    # else:
    #    return 0