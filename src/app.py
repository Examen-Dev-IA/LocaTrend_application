import os
import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd

st.title('Carte des valeurs foncières moyenne en France')

# Obtenez le répertoire du script
script_dir = os.path.dirname(os.path.abspath(__file__))

# # Charger le GeoJSON des départements avec Geopandas
# gdf = gpd.read_file('./datasets/geojson/departements.geojson')

# Construisez les chemins complets vers les fichiers GeoJSON et CSV
geojson_path = os.path.join(script_dir, 'datasets', 'geojson', 'departements.geojson')
csv_path = os.path.join(script_dir, 'datasets', 'csv', 'valeurs_foncieres_affichage.csv')

# Charger le GeoJSON des départements avec Geopandas
gdf = gpd.read_file(geojson_path)

# Charger le fichier CSV en utilisant seulement les colonnes spécifiées
df_paris = pd.read_csv(csv_path, encoding='utf-8', dtype={'code_commune': str, 'code_departement': str})

# Calculer les moyennes pour les colonnes spécifiées
avg_prices = df_paris.groupby('code_departement')['valeur_fonciere'].mean().reset_index()
avg_surface_bati = df_paris.groupby('code_departement')['surface_reelle_bati'].mean().reset_index()
avg_pieces_principales = df_paris.groupby('code_departement')['nombre_pieces_principales'].mean().reset_index()
avg_surface_terrain = df_paris.groupby('code_departement')['surface_terrain'].mean().reset_index()

# Fusionner les moyennes avec le GeoDataFrame des départements
gdf['valeur_fonciere_moyenne'] = gdf['code'].map(avg_prices.set_index('code_departement')['valeur_fonciere'])
gdf['surface_reelle_bati_avg'] = gdf['code'].map(avg_surface_bati.set_index('code_departement')['surface_reelle_bati'])
gdf['nombre_pieces_principales_avg'] = gdf['code'].map(avg_pieces_principales.set_index('code_departement')['nombre_pieces_principales'])
gdf['surface_terrain_avg'] = gdf['code'].map(avg_surface_terrain.set_index('code_departement')['surface_terrain'])

# Créer une carte avec Plotly Express pour les départements et la moyenne des prix fonciers
fig = px.choropleth_mapbox(gdf, 
                           geojson=gdf.geometry, 
                           locations=gdf.index, 
                           color='valeur_fonciere_moyenne',  # Utiliser la moyenne de la valeur foncière pour la couleur
                           color_continuous_scale="Viridis",
                           range_color=[gdf['valeur_fonciere_moyenne'].min(), gdf['valeur_fonciere_moyenne'].max()],
                           mapbox_style="carto-positron",
                           center={"lat": 46.6035, "lon": 1.8888},
                           zoom=5,
                           opacity=0.5,
                           custom_data=[gdf['code'], gdf['surface_reelle_bati_avg'], gdf['nombre_pieces_principales_avg'], gdf['surface_terrain_avg']],  # Ajouter les données au survol
                           )

# Personnaliser la carte (titre, etc.)
fig.update_layout(title="Carte des départements de la France")

# Ajouter les moyennes comme tooltips
fig.update_traces(hovertemplate="<br>".join([
    "Code: %{customdata[0]}",
    "Avg Surface Reelle Bati: %{customdata[1]}",
    "Avg Nombre Pieces Principales: %{customdata[2]}",
    "Avg Surface Terrain: %{customdata[3]}"
]))

st.plotly_chart(fig)