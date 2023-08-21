import mesa
import time

from .model import Habitacion, RobotLimpieza, Celda, Mueble, Cargador
from mesa.visualization.ModularVisualization import VisualizationElement
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter


MAX_NUMBER_ROBOTS = 20


def agent_portrayal(agent):
    if isinstance(agent, RobotLimpieza):
        return {
            "Shape": "circle",
            "Filled": "false",
            "Color": "Cyan",
            "Layer": 1,
            "r": 0.9,
            "text": f"{agent.carga}",
            "text_color": "black",
        }
    elif isinstance(agent, Mueble):
        return {
            "Shape": "rect",
            "Filled": "true",
            "Color": "black",
            "Layer": 0,
            "w": 0.9,
            "h": 0.9,
        }
    elif isinstance(agent, Celda):
        portrayal = {
            "Shape": "rect",
            "Filled": "true",
            "Layer": 0,
            "w": 0.9,
            "h": 0.9,
            "text_color": "Black",
        }
        if agent.sucia:
            portrayal["Color"] = "#ccbeaf"
            portrayal["text"] = "💩"
        else:
            portrayal["Color"] = "white"
            portrayal["text"] = ""
        return portrayal
    elif isinstance(agent, Cargador):
        portrayal = {
            "Shape": "rect",
            "Filled": "true",
            "Layer": 0,
            "w": 0.9,
            "h": 0.9,
            "text_color": "Black",
            "Color" : "green",
            "text" : "🔋",
        }
        return portrayal


grid = mesa.visualization.CanvasGrid(agent_portrayal, 20, 20, 400, 400)
chart_celdas = mesa.visualization.ChartModule(
    [{"Label": "CeldasSucias", "Color": "#36A2EB", "label": "Celdas Sucias"}],
    canvas_height=200,
    canvas_width=400,
    data_collector_name="datacollector",
)

class SimulationInfoChart(VisualizationElement):
    package_includes = ["Chart.min.js"]
    local_includes = ["js/simulation_info_element.js"]
    js_code = "window.SimulationInfoChart = function() {}"
    
    def __init__(self):
        self.series = []
        
    def render(self, model):
        simulation_info = model.get_simulation_info()
        self.series.append({
            "elapsed_time": simulation_info["elapsed_time"],
            "total_movements": simulation_info["total_movements"],
            "total_recharges": simulation_info["total_recharges"],
        })
        return self.series

visualization_elements = [
    grid,
    chart_celdas,
    SimulationInfoChart(),
]


model_params = {
    "num_agentes": mesa.visualization.Slider(
        "Número de Robots",
        5,  # Valor por defecto *5*
        2,  # Valor mínimo
        MAX_NUMBER_ROBOTS,  # Valor máximo
        1,  # Incremento
        description="Escoge cuántos robots deseas implementar en el modelo",
    ),
    "porc_celdas_sucias": mesa.visualization.Slider(
        "Porcentaje de Celdas Sucias",
        0.3, # Valor por defecto *0.3*
        0.1, # Valor mínimo
        0.75, # Valor máximo
        0.05, # Incremento
        description="Selecciona el porcentaje de celdas sucias",
    ),
    "porc_muebles": mesa.visualization.Slider(
        "Porcentaje de Muebles",
        0.1, # Valor por defecto *0.1*
        0.0,
        0.25,
        0.01,
        description="Selecciona el porcentaje de muebles",
    ),
    "modo_pos_inicial": mesa.visualization.Choice(
        "Posición Inicial de los Robots",
        "Aleatoria",
        ["Fija", "Aleatoria"],
        "Seleciona la forma se posicionan los robots",
    ),
    "M": 20,
    "N": 20,
}

server = mesa.visualization.ModularServer(
    Habitacion, visualization_elements, "botCleaner", model_params, 8521
)
server.launch()
print("Simulation has finished.")


