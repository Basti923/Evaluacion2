import urllib.parse
import requests

geocode_url = "https://graphhopper.com/api/1/geocode?"
route_url = "https://graphhopper.com/api/1/route?"

key = "9e77862b-37c9-4f31-babd-2cd41ceee6cf"


def geocodificacion(localizacion, key):
  """Función para obtener coordenadas (lat, lng) de una ubicación traducida al español."""
  while localizacion == "":
    localizacion = input(
        "\nPor favor, ingrese una ubicación válida ('s' o 'salir' para"
        " terminar): "
    ).strip()

  if localizacion.lower() in ("s", "salir", "q", "quit"):
    return 200, None, None, "salir"

  url = geocode_url + urllib.parse.urlencode(
      {"q": localizacion, "limit": 1, "key": key}
  )
  replydata = requests.get(url, timeout=30)
  json_data = replydata.json()
  json_status = replydata.status_code

  if json_status == 200 and json_data.get("hits"):
    hit = json_data["hits"][0]
    lat = hit["point"]["lat"]
    lng = hit["point"]["lng"]
    nombre = hit.get("name", localizacion)
    estado = hit.get("state", "")
    pais = hit.get("country", "")
    tipo_lugar = hit.get("osm_value", "desconocido")

    nueva_loc = ", ".join(
        parte for parte in (nombre, estado, pais) if parte
    )
    print(f"\n[URL de Geocodificación]: {url}")
    print(f"Ubicación encontrada: {nueva_loc} (Tipo de lugar: {tipo_lugar})")
    return json_status, lat, lng, nueva_loc
  else:
    print(
        "\nNo se encontraron coordenadas para:"
        f" {json_data.get('message', 'Sin coincidencias')}"
    )
    return json_status, None, None, localizacion


while True:
  print("\n" + "=" * 65)
  print("         SISTEMA DE NAVEGACIÓN Y RUTA EN ESPAÑOL - GRAPHHOPPER")
  print("=" * 65)
  print(
      "Perfiles de vehículo disponibles: 'car' (auto), 'bike' (bicicleta),"
      " 'foot' (a pie)"
  )

  vehiculo_input = (
      input(
          "\nIngrese el perfil de vehículo (o 's' / 'salir' para terminar): "
      )
      .strip()
      .lower()
  )

  if vehiculo_input in ("s", "salir", "q", "quit"):
    print("\n¡Gracias por utilizar el servicio de geolocalización! Hasta luego.")
    break

  if vehiculo_input not in ("car", "bike", "foot"):
    print(
        "\n[AVISO] No se ingresó un perfil válido. Se utilizará 'car' (auto) por"
        " defecto."
    )
    vehiculo = "car"
  else:
    vehiculo = vehiculo_input

  loc_origen = input(
      "\nIngrese la ubicación de ORIGEN (o 's' / 'salir' para terminar): "
  ).strip()
  if loc_origen.lower() in ("s", "salir", "q", "quit"):
    print("\nSaliendo del programa...")
    break

  orig = geocodificacion(loc_origen, key)
  if orig[3] == "salir" or orig[0] != 200 or orig[1] is None:
    if orig[3] == "salir":
      print("\nSaliendo del programa...")
      break
    continue

  loc_destino = input(
      "\nIngrese la ubicación de DESTINO (o 's' / 'salir' para terminar): "
  ).strip()
  if loc_destino.lower() in ("s", "salir", "q", "quit"):
    print("\nSaliendo del programa...")
    break

  dest = geocodificacion(loc_destino, key)
  if dest[3] == "salir" or dest[0] != 200 or dest[1] is None:
    if dest[3] == "salir":
      print("\nSaliendo del programa...")
      break
    continue

  print("\n[PROCESANDO] Calculando la mejor ruta...")

  puntos = f"point={orig[1]},{orig[2]}&point={dest[1]},{dest[2]}"
  params = (
      f"key={key}&profile={vehiculo}&{puntos}&instructions=true&locale=es"
  )
  url_rutas = route_url + params

  replydata_ruta = requests.get(url_rutas, timeout=30)
  estado_ruta = replydata_ruta.status_code
  datos_ruta = replydata_ruta.json()

  print(f"Código de Estado HTTP: {estado_ruta}")
  print(f"URL de Enrutamiento: {url_rutas}\n")

  if estado_ruta != 200:
    print(
        "Error en la consulta de ruta:"
        f" {datos_ruta.get('message', 'Error desconocido')}"
    )
    continue

  if not datos_ruta.get("paths"):
    print("No se encontró ninguna ruta entre los puntos indicados.")
    continue

  ruta = datos_ruta["paths"][0]

  distancia_km = ruta["distance"] / 1000.0
  distancia_millas = distancia_km / 1.60934

  segundos_totales = int(ruta["time"] / 1000)
  horas = segundos_totales // 3600
  minutos = (segundos_totales % 3600) // 60
  segundos = segundos_totales % 60

  print("*" * 65)
  print(f" RESUMEN DEL VIAJE: Desde [{orig[3]}] hasta [{dest[3]}]")
  print(f" Medio de transporte: {vehiculo.upper()}")
  print(
      f" Distancia total: {distancia_km:.2f} km ({distancia_millas:.2f} millas)"
  )
  print(f" Tiempo estimado de viaje: {horas:02d}h:{minutos:02d}m:{segundos:02d}s")
  print("*" * 65)

  print("\n--- NARRATIVA DEL VIAJE (INSTRUCCIONES PASO A PASO EN ESPAÑOL) ---")
  for i, instruccion in enumerate(ruta.get("instructions", []), 1):
    texto = instruccion.get("text", "")
    d_m = instruccion.get("distance", 0)
    d_km = d_m / 1000.0
    d_mi = d_km / 1.60934
    print(f"{i:2d}. {texto} ({d_km:.2f} km / {d_mi:.2f} mi)")

  print("-" * 65)
