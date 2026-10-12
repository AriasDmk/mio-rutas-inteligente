import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def ejecutar_clustering():
    # 1. Cargar el dataset no supervisado
    ruta_csv = "datos/dataset_no_supervisado.csv"
    print(f"Cargando datos desde: {ruta_csv}")
    df = pd.read_csv(ruta_csv)

    # 2. Seleccionar características cuantitativas para el agrupamiento
    features = ['promedio_pasajeros_dia', 'tiempo_espera_promedio_min', 'conexiones_disponibles', 'indice_congestion']
    X = df[features]

    # 3. Normalizar los datos para que tengan la misma escala
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 4. Aplicar el modelo de aprendizaje no supervisado K-Means (agrupando en 3 clústeres)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_scaled)

    # 5. Mostrar resultados en consola
    print("\n--- RESULTADOS DEL MODELO K-MEANS (CLUSTERING DE ESTACIONES) ---")
    print(df[['estacion', 'cluster', 'indice_congestion']])
    print("\nCentroides de los clústeres (valores normalizados):")
    print(kmeans.cluster_centers_)

if __name__ == "__main__":
    ejecutar_clustering()
    