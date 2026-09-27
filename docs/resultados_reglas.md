# Resultados: base de conocimiento y motor de inferencia
Autor: José Luis Arias

## 1. Reglas R3 y R4: negación por fallo y estación cerrada

### Prueba 1: sin estaciones cerradas
```
python main.py consultar "disponible(t40, belalcazar, R, T)"
R = floresta, T = 2.1
R = san_pascual, T = 2.3
```
### Análisis
**Qué hice:** Se ejecuta este comando preguntando al sistema a que estaciones  puede ir la ruta T40 desde belalcazar y que mde  diga cuanto se demora.
**Cual fue el resultado:** Sale 2 estaciones: Floresta (2,1 min) y san pascual (2,3 min).
**Por qué:** La regla R3 dice que un tramo está disponible si ninguna de ses estaciones está cerrada. Como en la base no hay ningún hecho 'cerrada(), el sistema no puee demostrar que alguna está cerrada y las da por abiertas. Esto es la negacion por fallo('\+'): Lo que no se puede desmostrar se toma como falso. Por eso no hace falta escribir que cada estación está abierta; solo se registran los cierres.

### Prueba 2: con San Pascual cerrada
```
python main.py consultar "disponible(t40, belalcazar, R, T)" --cerrar san_pascual
R = floresta, T = 2.1
R = centro, T = 4.6
```
**Qué hice:** La misma pregunta pero cerrando la estacion de  San Pascual.
**Cual fue el resultado.** San pascual desapareció y apareció Centro con 4,6 min. Floresta no cambio.
**Por qué:** San pascual desapareció porque ahora  existe el hecho 'cerradas(san pacsual)'. La condición '\+ cerrada(B)de la regla R3 ya no se cumple y el tramo deja de estar disponible.
- Centro apareció por la regla R4: si una estacion está cerrada, el bus pasa sin detenerse. El sistema unio los 2 tramos Belalcazar  → San pascual (2,3 min) y San pascual  → Centro (2,3 min) en uno solo tramo de 4,6 min, el Viaje no es mas largo simplemente no para en san pascual.

**Conclusion**
Con solo agregar un hecho (`cerrada(san_pascual)`) el sistema cambió su comportamiento
sin tocar el código. Eso muestra la ventaja de tener el conocimiento en reglas: las
conclusiones se recalculan solas cuando cambian los hechos.



