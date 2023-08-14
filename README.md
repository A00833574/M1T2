# M1T2
Actividad Sistema de Barredoras

Doña Martha (quien ya está retirada y solo quiere terminar de escribir su novela) tiene un conjunto de P robots limpiadores, no tan sofisticados e inteligente, pero de cierta manera ellos cumplen su tarea. Normalmente ellos se utilizan en una habitación de M x N espacios o celdas, en donde cierto porcentaje de ellas están sucias y otro porcentaje, mucho menor, tiene muebles o cajas que impiden a los robots posicionarse en ellas. Un detalle bastante curioso con los robots es que, a pesar de tener baterías, se descargan con facilidad y no tienen un puesto de carga en la habitación.

Su actual propietaria está cansadísima de recogerlos y ponerlos a cargar en otra habitación, por ello decide contactar a un(a) especialista en sistemas multi-agente, como tú. La tarea es sencilla:

Colocar, al menos, una estación de carga por cada (M x N)/4 celdas.
Reprogramar cada robot para que incrementen su eficiencia y no malgasten su batería realizando movimiento innecesarios.
Ten en cuenta que los robots no se comunican entre sí (no está en su programa actual), pero tienen un excelente módulo ZigBee que les permite realizar esta tarea.
Define un umbral para evitar la descarga completa: Recuerda que si un robot llega a cero (0), éste no se moverá por su cuenta.
Observando el datasheet de las baterías y los cargadores, sabes que a los robots les toma dos (2) unidades de tiempo (steps) por un 50% de carga. 

Ahora bien, una vez realizada la implementación, Doña Martha, quien en realidad es Ingeniera en Robótica y Especialista en Sistemas Autónomos, desea leer tu informe técnico. Éste debe tener lo siguiente:

Tiempo necesario hasta que todas las celdas estén limpias.
Número de movimientos realizados por todos los agentes.
Cantidad de recargas completas, directamente relacionadas con el consumo de energía eléctrica.
Incluye el diagrama de tu máquina de estados del agente.
Analiza cómo la cantidad de agentes impacta el tiempo dedicado y el consumo energético que esto implica.