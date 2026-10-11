import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report

print("--- CARGANDO FUENTE DE DATOS ---")
df = pd.read_csv("datos/dataset_transporte.csv")
print(df.head())

X = df[['distancia_km', 'transbordos', 'tiempo_viaje_min']]
y = df['hora_pico']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("\n--- ENTRENANDO MODELO (ÁRBOL DE DECISIÓN) ---")
modelo = DecisionTreeClassifier(random_state=42)
modelo.fit(X_train, y_train)

predicciones = modelo.predict(X_test)

print("\n--- RESULTADOS ---")
print("Precisión:", accuracy_score(y_test, predicciones))
print("\nReporte:\n", classification_report(y_test, predicciones, zero_division=0))