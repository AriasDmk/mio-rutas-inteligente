% =====================================================================
%  BASE DE CONOCIMIENTO - Sistema de transporte masivo MIO (Cali)
%  GENERADA por herramientas/construir_base.py a partir de datos reales
%  del SIUR: https://servicios.siur.com.co/buscarutas/ (api/paradas.php y api/recorrido.php)
%  Fecha de descarga: 2026-09-26
%  Supuestos: velocidad troncal 20 km/h, expreso 24 km/h;
%             frecuencia troncal 8 min, expreso 10 min.
%
%  Sintaxis tipo Prolog (cláusulas de Horn). Variables en mayúscula.
%  \+ = negación por fallo.
% =====================================================================

% ---- HECHOS: estaciones (81)  estacion(Id, 'Nombre') ----
estacion(aguablanca, 'Aguablanca').
estacion(alamos, 'Álamos').
estacion(alfonso_lopez, 'Alfonso López').
estacion(amanecer, 'Amanecer').
estacion(andres_sanin, 'Andrés Sanín').
estacion(antonio_narino, 'Antonio Nariño').
estacion(atanasio_girardot, 'Atanasio Girardot').
estacion(belalcazar, 'Belalcázar').
estacion(buitrera, 'Buitrera').
estacion(caldas, 'Caldas').
estacion(calima, 'Calima').
estacion(calipso, 'Calipso').
estacion(canaverales, 'Cañaverales').
estacion(capri, 'Capri').
estacion(centro, 'Centro').
estacion(chapinero, 'Chapinero').
estacion(chiminangos, 'Chiminangos').
estacion(cien_palos, 'Cien Palos').
estacion(ciudad_modelo, 'Ciudad Modelo').
estacion(conquistadores, 'Conquistadores').
estacion(e_7_de_agosto, '7 de Agosto').
estacion(el_diamante, 'El Diamante').
estacion(el_pondaje, 'El Pondaje').
estacion(el_trebol, 'El Trébol').
estacion(estadio, 'Estadio').
estacion(fatima, 'Fátima').
estacion(flora_industrial, 'Flora Industrial').
estacion(floresta, 'Floresta').
estacion(guadalupe, 'Guadalupe').
estacion(jorge_eliecer_gaitan, 'Jorge Eliécer Gaitán').
estacion(la_ermita, 'La Ermita').
estacion(la_rivera, 'La Rivera').
estacion(las_americas, 'Las Américas').
estacion(las_ceibas, 'Las Ceibas').
estacion(lido, 'Lido').
estacion(lleras_restrepo, 'Lleras Restrepo').
estacion(los_alcazares, 'Los Alcázares').
estacion(los_guaduales, 'Los Guaduales').
estacion(los_pinos, 'Los Pinos').
estacion(manzana_del_saber, 'Manzana del Saber').
estacion(manzanares, 'Manzanares').
estacion(mariano_ramos, 'Mariano Ramos').
estacion(melendez, 'Meléndez').
estacion(menga, 'Menga').
estacion(metropolitano_del_norte, 'Metropolitano del Norte').
estacion(nueva_base, 'Nueva Base').
estacion(nueva_floresta, 'Nueva Floresta').
estacion(nuevo_latir, 'Nuevo Latir').
estacion(pampalinda, 'Pampalinda').
estacion(paso_del_comercio, 'Paso del Comercio').
estacion(petecuy, 'Petecuy').
estacion(piloto_colombina, 'Piloto Colombina').
estacion(plaza_de_cayzedo, 'Plaza de Cayzedo').
estacion(popular, 'Popular').
estacion(prados_del_norte, 'Prados del Norte').
estacion(primitivo, 'Primitivo').
estacion(refugio, 'Refugio').
estacion(republica_de_israel, 'República de Israel').
estacion(rio_cali, 'Río Cali').
estacion(salomia, 'Salomia').
estacion(san_bosco, 'San Bosco').
estacion(san_luis, 'San Luis').
estacion(san_nicolas, 'San Nicolás').
estacion(san_pascual, 'San Pascual').
estacion(san_pedro, 'San Pedro').
estacion(santa_librada, 'Santa Librada').
estacion(santa_monica, 'Santa Mónica').
estacion(simon_bolivar, 'Simón Bolívar').
estacion(tequendama, 'Tequendama').
estacion(torre_de_cali, 'Torre de Cali').
estacion(troncal_unida, 'Troncal Unida').
estacion(ulpiano_lloreda, 'Ulpiano Lloreda').
estacion(unidad_deportiva, 'Unidad Deportiva').
estacion(univalle, 'Univalle').
estacion(universidades, 'Universidades').
estacion(versalles, 'Versalles').
estacion(villa_del_lago, 'Villa del Lago').
estacion(villa_del_sur, 'Villa del Sur').
estacion(villacolombia, 'Villacolombia').
estacion(villanueva, 'Villanueva').
estacion(vipasa, 'Vipasa').

% ---- HECHOS: terminales (transbordo integrado, más rápido) ----
terminal(aguablanca).
terminal(andres_sanin).
terminal(menga).
terminal(paso_del_comercio).
terminal(simon_bolivar).
terminal(universidades).

% ---- HECHOS: coordenadas  coordenada(Id, Latitud, Longitud) ----
coordenada(aguablanca, 3.4143, -76.48151).
coordenada(alamos, 3.4846, -76.51325).
coordenada(alfonso_lopez, 3.46395, -76.48374).
coordenada(amanecer, 3.42152, -76.49073).
coordenada(andres_sanin, 3.44338, -76.48345).
coordenada(antonio_narino, 3.41895, -76.50863).
coordenada(atanasio_girardot, 3.44476, -76.5082).
coordenada(belalcazar, 3.44414, -76.52061).
coordenada(buitrera, 3.3728, -76.54038).
coordenada(caldas, 3.39386, -76.54591).
coordenada(calima, 3.48634, -76.49643).
coordenada(calipso, 3.42728, -76.49984).
coordenada(canaverales, 3.40206, -76.52302).
coordenada(capri, 3.38777, -76.54484).
coordenada(centro, 3.44865, -76.53017).
coordenada(chapinero, 3.44425, -76.50215).
coordenada(chiminangos, 3.48146, -76.4983).
coordenada(cien_palos, 3.43982, -76.52274).
coordenada(ciudad_modelo, 3.41684, -76.51082).
coordenada(conquistadores, 3.42716, -76.50545).
coordenada(e_7_de_agosto, 3.44516, -76.48725).
coordenada(el_diamante, 3.42294, -76.50447).
coordenada(el_pondaje, 3.43042, -76.49759).
coordenada(el_trebol, 3.44349, -76.49591).
coordenada(estadio, 3.43164, -76.54325).
coordenada(fatima, 3.46296, -76.51728).
coordenada(flora_industrial, 3.47831, -76.50217).
coordenada(floresta, 3.44522, -76.5145).
coordenada(guadalupe, 3.40977, -76.54746).
coordenada(jorge_eliecer_gaitan, 3.46868, -76.48522).
coordenada(la_ermita, 3.45368, -76.53165).
coordenada(la_rivera, 3.47378, -76.48682).
coordenada(las_americas, 3.46369, -76.52519).
coordenada(las_ceibas, 3.45574, -76.48452).
coordenada(lido, 3.4191, -76.54834).
coordenada(lleras_restrepo, 3.43794, -76.49379).
coordenada(los_alcazares, 3.48544, -76.49365).
coordenada(los_guaduales, 3.48745, -76.49998).
coordenada(los_pinos, 3.45953, -76.48287).
coordenada(manzana_del_saber, 3.43479, -76.54107).
coordenada(manzanares, 3.4663, -76.51325).
coordenada(mariano_ramos, 3.40686, -76.5213).
coordenada(melendez, 3.37723, -76.54282).
coordenada(menga, 3.48953, -76.50861).
coordenada(metropolitano_del_norte, 3.48335, -76.48994).
coordenada(nueva_base, 3.44894, -76.48813).
coordenada(nueva_floresta, 3.43347, -76.49608).
coordenada(nuevo_latir, 3.41857, -76.48701).
coordenada(pampalinda, 3.40386, -76.54681).
coordenada(paso_del_comercio, 3.49069, -76.49159).
coordenada(petecuy, 3.44864, -76.52774).
coordenada(piloto_colombina, 3.4601, -76.52246).
coordenada(plaza_de_cayzedo, 3.45243, -76.53131).
coordenada(popular, 3.46968, -76.51064).
coordenada(prados_del_norte, 3.47456, -76.51951).
coordenada(primitivo, 3.43732, -76.51767).
coordenada(refugio, 3.39882, -76.54647).
coordenada(republica_de_israel, 3.41213, -76.51573).
coordenada(rio_cali, 3.46045, -76.52527).
coordenada(salomia, 3.47383, -76.50661).
coordenada(san_bosco, 3.44223, -76.53265).
coordenada(san_luis, 3.47682, -76.48778).
coordenada(san_nicolas, 3.45855, -76.52569).
coordenada(san_pascual, 3.44258, -76.52689).
coordenada(san_pedro, 3.45403, -76.52987).
coordenada(santa_librada, 3.4396, -76.53718).
coordenada(santa_monica, 3.43455, -76.51392).
coordenada(simon_bolivar, 3.39749, -76.52351).
coordenada(tequendama, 3.42376, -76.54691).
coordenada(torre_de_cali, 3.45667, -76.53031).
coordenada(troncal_unida, 3.42465, -76.4944).
coordenada(ulpiano_lloreda, 3.44594, -76.48957).
coordenada(unidad_deportiva, 3.41483, -76.54828).
coordenada(univalle, 3.37093, -76.53684).
coordenada(universidades, 3.367, -76.5292).
coordenada(versalles, 3.46117, -76.52708).
coordenada(villa_del_lago, 3.4408, -76.49223).
coordenada(villa_del_sur, 3.41045, -76.51748).
coordenada(villacolombia, 3.44381, -76.49877).
coordenada(villanueva, 3.43212, -76.51035).
coordenada(vipasa, 3.47871, -76.51693).

% ---- HECHOS: rutas  ruta(Id, 'Código', Tipo)  y frecuencia(Id, Min) ----
ruta(t31, 'T31', troncal).
ruta(t40, 'T40', troncal).
ruta(t47, 'T47', troncal).
ruta(t50, 'T50', troncal).
ruta(t57, 'T57', troncal).
ruta(t62, 'T62', troncal).
ruta(t12, 'T12', troncal).
ruta(e21, 'E21', expreso).
ruta(e37, 'E37', expreso).
frecuencia(t31, 8).
frecuencia(t40, 8).
frecuencia(t47, 8).
frecuencia(t50, 8).
frecuencia(t57, 8).
frecuencia(t62, 8).
frecuencia(t12, 8).
frecuencia(e21, 10).
frecuencia(e37, 10).

% ---- HECHOS: tramos dirigidos (310)  tramo(Ruta, Desde, Hasta, Minutos) ----
% T31
tramo(t31, paso_del_comercio, flora_industrial, 6.0).
tramo(t31, flora_industrial, salomia, 2.1).
tramo(t31, salomia, popular, 1.9).
tramo(t31, popular, manzanares, 1.4).
tramo(t31, manzanares, fatima, 1.8).
tramo(t31, fatima, piloto_colombina, 2.0).
tramo(t31, piloto_colombina, san_nicolas, 1.2).
tramo(t31, san_nicolas, torre_de_cali, 1.8).
tramo(t31, torre_de_cali, san_pedro, 0.9).
tramo(t31, san_pedro, petecuy, 2.0).
tramo(t31, petecuy, san_pascual, 2.4).
tramo(t31, san_pascual, san_bosco, 1.9).
tramo(t31, san_bosco, santa_librada, 1.8).
tramo(t31, santa_librada, manzana_del_saber, 2.1).
tramo(t31, manzana_del_saber, estadio, 1.3).
tramo(t31, estadio, tequendama, 2.9).
tramo(t31, tequendama, lido, 1.6).
tramo(t31, lido, unidad_deportiva, 1.4).
tramo(t31, unidad_deportiva, guadalupe, 1.7).
tramo(t31, guadalupe, pampalinda, 2.0).
tramo(t31, pampalinda, refugio, 1.7).
tramo(t31, refugio, caldas, 1.7).
tramo(t31, caldas, capri, 2.1).
tramo(t31, capri, melendez, 3.6).
tramo(t31, melendez, buitrera, 1.8).
tramo(t31, buitrera, univalle, 1.4).
tramo(t31, univalle, universidades, 3.3).
tramo(t31, universidades, univalle, 2.8).
tramo(t31, univalle, buitrera, 1.3).
tramo(t31, buitrera, melendez, 1.9).
tramo(t31, melendez, capri, 3.6).
tramo(t31, capri, caldas, 2.2).
tramo(t31, caldas, refugio, 1.5).
tramo(t31, refugio, pampalinda, 1.7).
tramo(t31, pampalinda, guadalupe, 2.0).
tramo(t31, guadalupe, unidad_deportiva, 1.8).
tramo(t31, unidad_deportiva, lido, 1.4).
tramo(t31, lido, tequendama, 1.7).
tramo(t31, tequendama, estadio, 2.9).
tramo(t31, estadio, manzana_del_saber, 1.3).
tramo(t31, manzana_del_saber, santa_librada, 2.1).
tramo(t31, santa_librada, san_bosco, 1.8).
tramo(t31, san_bosco, centro, 3.4).
tramo(t31, centro, la_ermita, 1.8).
tramo(t31, la_ermita, torre_de_cali, 1.1).
tramo(t31, torre_de_cali, rio_cali, 2.3).
tramo(t31, rio_cali, fatima, 3.2).
tramo(t31, fatima, manzanares, 1.7).
tramo(t31, manzanares, popular, 1.4).
tramo(t31, popular, salomia, 1.9).
tramo(t31, salomia, flora_industrial, 2.1).
tramo(t31, flora_industrial, chiminangos, 1.7).
tramo(t31, chiminangos, paso_del_comercio, 3.8).
% T40
tramo(t40, andres_sanin, e_7_de_agosto, 3.9).
tramo(t40, e_7_de_agosto, el_trebol, 3.1).
tramo(t40, el_trebol, villacolombia, 1.0).
tramo(t40, villacolombia, chapinero, 1.1).
tramo(t40, chapinero, atanasio_girardot, 2.0).
tramo(t40, atanasio_girardot, floresta, 2.1).
tramo(t40, floresta, belalcazar, 2.1).
tramo(t40, belalcazar, san_pascual, 2.3).
tramo(t40, san_pascual, centro, 2.3).
tramo(t40, centro, la_ermita, 1.8).
tramo(t40, la_ermita, san_pedro, 1.4).
tramo(t40, san_pedro, petecuy, 1.9).
tramo(t40, petecuy, belalcazar, 4.2).
tramo(t40, belalcazar, floresta, 2.1).
tramo(t40, floresta, atanasio_girardot, 2.1).
tramo(t40, atanasio_girardot, chapinero, 2.0).
tramo(t40, chapinero, villacolombia, 1.1).
tramo(t40, villacolombia, el_trebol, 1.0).
tramo(t40, el_trebol, e_7_de_agosto, 3.0).
tramo(t40, e_7_de_agosto, andres_sanin, 3.5).
% T47
tramo(t47, andres_sanin, e_7_de_agosto, 4.2).
tramo(t47, e_7_de_agosto, el_trebol, 3.1).
tramo(t47, el_trebol, villacolombia, 1.0).
tramo(t47, villacolombia, chapinero, 1.1).
tramo(t47, chapinero, atanasio_girardot, 2.0).
tramo(t47, atanasio_girardot, floresta, 2.1).
tramo(t47, floresta, belalcazar, 2.1).
tramo(t47, belalcazar, san_pascual, 2.3).
tramo(t47, san_pascual, san_bosco, 1.6).
tramo(t47, san_bosco, santa_librada, 1.7).
tramo(t47, santa_librada, manzana_del_saber, 2.2).
tramo(t47, manzana_del_saber, estadio, 1.3).
tramo(t47, estadio, tequendama, 3.2).
tramo(t47, tequendama, lido, 1.6).
tramo(t47, lido, unidad_deportiva, 1.4).
tramo(t47, unidad_deportiva, lido, 1.7).
tramo(t47, lido, tequendama, 1.7).
tramo(t47, tequendama, estadio, 3.2).
tramo(t47, estadio, manzana_del_saber, 1.3).
tramo(t47, manzana_del_saber, santa_librada, 2.2).
tramo(t47, santa_librada, san_bosco, 1.7).
tramo(t47, san_bosco, san_pascual, 1.7).
tramo(t47, san_pascual, belalcazar, 2.3).
tramo(t47, belalcazar, floresta, 2.1).
tramo(t47, floresta, atanasio_girardot, 2.1).
tramo(t47, atanasio_girardot, chapinero, 2.0).
tramo(t47, chapinero, villacolombia, 1.1).
tramo(t47, villacolombia, el_trebol, 1.0).
tramo(t47, el_trebol, e_7_de_agosto, 3.0).
tramo(t47, e_7_de_agosto, andres_sanin, 3.4).
% T50
tramo(t50, aguablanca, nuevo_latir, 3.9).
tramo(t50, nuevo_latir, amanecer, 1.6).
tramo(t50, amanecer, troncal_unida, 1.6).
tramo(t50, troncal_unida, calipso, 2.4).
tramo(t50, calipso, conquistadores, 2.6).
tramo(t50, conquistadores, villanueva, 2.4).
tramo(t50, villanueva, santa_monica, 1.4).
tramo(t50, santa_monica, primitivo, 1.6).
tramo(t50, primitivo, cien_palos, 1.9).
tramo(t50, cien_palos, san_pascual, 2.1).
tramo(t50, san_pascual, centro, 2.2).
tramo(t50, centro, la_ermita, 1.8).
tramo(t50, la_ermita, san_pedro, 1.6).
tramo(t50, san_pedro, petecuy, 1.9).
tramo(t50, petecuy, cien_palos, 3.7).
tramo(t50, cien_palos, primitivo, 1.9).
tramo(t50, primitivo, santa_monica, 1.6).
tramo(t50, santa_monica, villanueva, 1.4).
tramo(t50, villanueva, conquistadores, 2.4).
tramo(t50, conquistadores, calipso, 2.7).
tramo(t50, calipso, troncal_unida, 2.4).
tramo(t50, troncal_unida, amanecer, 1.6).
tramo(t50, amanecer, nuevo_latir, 1.6).
tramo(t50, nuevo_latir, aguablanca, 2.5).
% T57
tramo(t57, aguablanca, nuevo_latir, 4.0).
tramo(t57, nuevo_latir, amanecer, 1.6).
tramo(t57, amanecer, troncal_unida, 1.6).
tramo(t57, troncal_unida, calipso, 2.4).
tramo(t57, calipso, conquistadores, 2.6).
tramo(t57, conquistadores, villanueva, 2.4).
tramo(t57, villanueva, santa_monica, 1.4).
tramo(t57, santa_monica, primitivo, 1.6).
tramo(t57, primitivo, cien_palos, 1.9).
tramo(t57, cien_palos, san_pascual, 2.1).
tramo(t57, san_pascual, san_bosco, 1.5).
tramo(t57, san_bosco, santa_librada, 1.7).
tramo(t57, santa_librada, manzana_del_saber, 2.2).
tramo(t57, manzana_del_saber, estadio, 1.3).
tramo(t57, estadio, tequendama, 3.2).
tramo(t57, tequendama, lido, 1.6).
tramo(t57, lido, unidad_deportiva, 1.1).
tramo(t57, unidad_deportiva, lido, 1.9).
tramo(t57, lido, tequendama, 1.7).
tramo(t57, tequendama, estadio, 3.2).
tramo(t57, estadio, manzana_del_saber, 1.3).
tramo(t57, manzana_del_saber, santa_librada, 2.2).
tramo(t57, santa_librada, san_bosco, 1.7).
tramo(t57, san_bosco, san_pascual, 1.7).
tramo(t57, san_pascual, cien_palos, 2.1).
tramo(t57, cien_palos, primitivo, 1.9).
tramo(t57, primitivo, santa_monica, 1.6).
tramo(t57, santa_monica, villanueva, 1.4).
tramo(t57, villanueva, conquistadores, 2.4).
tramo(t57, conquistadores, calipso, 2.3).
tramo(t57, calipso, troncal_unida, 2.8).
tramo(t57, troncal_unida, amanecer, 1.6).
tramo(t57, amanecer, nuevo_latir, 1.6).
tramo(t57, nuevo_latir, aguablanca, 2.4).
% T62
tramo(t62, simon_bolivar, canaverales, 2.5).
tramo(t62, canaverales, mariano_ramos, 1.7).
tramo(t62, mariano_ramos, villa_del_sur, 1.8).
tramo(t62, villa_del_sur, republica_de_israel, 0.8).
tramo(t62, republica_de_israel, ciudad_modelo, 2.2).
tramo(t62, ciudad_modelo, antonio_narino, 1.0).
tramo(t62, antonio_narino, el_diamante, 1.9).
tramo(t62, el_diamante, calipso, 2.0).
tramo(t62, calipso, conquistadores, 3.8).
tramo(t62, conquistadores, villanueva, 2.4).
tramo(t62, villanueva, santa_monica, 1.4).
tramo(t62, santa_monica, primitivo, 1.6).
tramo(t62, primitivo, cien_palos, 1.9).
tramo(t62, cien_palos, san_pascual, 2.1).
tramo(t62, san_pascual, centro, 2.2).
tramo(t62, centro, la_ermita, 1.8).
tramo(t62, la_ermita, torre_de_cali, 1.3).
tramo(t62, torre_de_cali, versalles, 1.9).
tramo(t62, versalles, torre_de_cali, 10.2).
tramo(t62, torre_de_cali, san_pedro, 1.0).
tramo(t62, san_pedro, petecuy, 1.9).
tramo(t62, petecuy, cien_palos, 3.9).
tramo(t62, cien_palos, primitivo, 1.9).
tramo(t62, primitivo, santa_monica, 1.6).
tramo(t62, santa_monica, villanueva, 1.4).
tramo(t62, villanueva, conquistadores, 2.4).
tramo(t62, conquistadores, calipso, 2.6).
tramo(t62, calipso, el_diamante, 3.5).
tramo(t62, el_diamante, antonio_narino, 1.8).
tramo(t62, antonio_narino, ciudad_modelo, 0.9).
tramo(t62, ciudad_modelo, republica_de_israel, 2.1).
tramo(t62, republica_de_israel, villa_del_sur, 1.0).
tramo(t62, villa_del_sur, mariano_ramos, 1.6).
tramo(t62, mariano_ramos, canaverales, 1.8).
tramo(t62, canaverales, simon_bolivar, 1.5).
% T12
tramo(t12, menga, los_guaduales, 3.3).
tramo(t12, los_guaduales, calima, 1.3).
tramo(t12, calima, los_alcazares, 1.0).
tramo(t12, los_alcazares, metropolitano_del_norte, 1.5).
tramo(t12, metropolitano_del_norte, san_luis, 2.3).
tramo(t12, san_luis, la_rivera, 1.1).
tramo(t12, la_rivera, jorge_eliecer_gaitan, 1.8).
tramo(t12, jorge_eliecer_gaitan, alfonso_lopez, 1.6).
tramo(t12, alfonso_lopez, los_pinos, 1.5).
tramo(t12, los_pinos, las_ceibas, 1.4).
tramo(t12, las_ceibas, nueva_base, 2.6).
tramo(t12, nueva_base, ulpiano_lloreda, 1.1).
tramo(t12, ulpiano_lloreda, villa_del_lago, 1.9).
tramo(t12, villa_del_lago, lleras_restrepo, 1.1).
tramo(t12, lleras_restrepo, nueva_floresta, 1.7).
tramo(t12, nueva_floresta, el_pondaje, 1.1).
tramo(t12, el_pondaje, calipso, 1.4).
tramo(t12, calipso, el_diamante, 2.4).
tramo(t12, el_diamante, antonio_narino, 1.8).
tramo(t12, antonio_narino, ciudad_modelo, 0.9).
tramo(t12, ciudad_modelo, republica_de_israel, 2.1).
tramo(t12, republica_de_israel, villa_del_sur, 1.0).
tramo(t12, villa_del_sur, mariano_ramos, 1.6).
tramo(t12, mariano_ramos, canaverales, 1.8).
tramo(t12, canaverales, simon_bolivar, 1.6).
tramo(t12, simon_bolivar, universidades, 12.1).
tramo(t12, universidades, simon_bolivar, 11.7).
tramo(t12, simon_bolivar, canaverales, 1.5).
tramo(t12, canaverales, mariano_ramos, 1.7).
tramo(t12, mariano_ramos, villa_del_sur, 1.8).
tramo(t12, villa_del_sur, republica_de_israel, 0.8).
tramo(t12, republica_de_israel, ciudad_modelo, 2.2).
tramo(t12, ciudad_modelo, antonio_narino, 1.0).
tramo(t12, antonio_narino, el_diamante, 1.9).
tramo(t12, el_diamante, calipso, 2.0).
tramo(t12, calipso, el_pondaje, 1.3).
tramo(t12, el_pondaje, nueva_floresta, 1.2).
tramo(t12, nueva_floresta, lleras_restrepo, 1.6).
tramo(t12, lleras_restrepo, villa_del_lago, 1.2).
tramo(t12, villa_del_lago, ulpiano_lloreda, 1.8).
tramo(t12, ulpiano_lloreda, nueva_base, 1.1).
tramo(t12, nueva_base, las_ceibas, 2.6).
tramo(t12, las_ceibas, los_pinos, 1.2).
tramo(t12, los_pinos, alfonso_lopez, 1.5).
tramo(t12, alfonso_lopez, jorge_eliecer_gaitan, 1.6).
tramo(t12, jorge_eliecer_gaitan, la_rivera, 1.8).
tramo(t12, la_rivera, san_luis, 1.2).
tramo(t12, san_luis, metropolitano_del_norte, 2.2).
tramo(t12, metropolitano_del_norte, los_alcazares, 1.7).
tramo(t12, los_alcazares, calima, 0.6).
tramo(t12, calima, los_guaduales, 1.3).
tramo(t12, los_guaduales, menga, 3.2).
% E21
tramo(e21, menga, alamos, 2.3).
tramo(e21, alamos, vipasa, 1.9).
tramo(e21, vipasa, prados_del_norte, 1.4).
tramo(e21, prados_del_norte, las_americas, 3.6).
tramo(e21, las_americas, versalles, 0.8).
tramo(e21, versalles, torre_de_cali, 1.5).
tramo(e21, torre_de_cali, san_pedro, 0.8).
tramo(e21, san_pedro, petecuy, 1.6).
tramo(e21, petecuy, san_pascual, 2.1).
tramo(e21, san_pascual, san_bosco, 1.6).
tramo(e21, san_bosco, santa_librada, 1.5).
tramo(e21, santa_librada, estadio, 2.8).
tramo(e21, estadio, tequendama, 2.4).
tramo(e21, tequendama, unidad_deportiva, 2.5).
tramo(e21, unidad_deportiva, pampalinda, 3.1).
tramo(e21, pampalinda, caldas, 2.8).
tramo(e21, caldas, capri, 1.7).
tramo(e21, capri, melendez, 3.0).
tramo(e21, melendez, buitrera, 1.5).
tramo(e21, buitrera, universidades, 3.8).
tramo(e21, universidades, buitrera, 3.4).
tramo(e21, buitrera, melendez, 1.6).
tramo(e21, melendez, capri, 3.0).
tramo(e21, capri, caldas, 1.9).
tramo(e21, caldas, pampalinda, 2.6).
tramo(e21, pampalinda, unidad_deportiva, 3.1).
tramo(e21, unidad_deportiva, tequendama, 2.5).
tramo(e21, tequendama, estadio, 2.4).
tramo(e21, estadio, santa_librada, 2.8).
tramo(e21, santa_librada, san_bosco, 1.5).
tramo(e21, san_bosco, centro, 2.8).
tramo(e21, centro, plaza_de_cayzedo, 1.1).
tramo(e21, plaza_de_cayzedo, torre_de_cali, 1.3).
tramo(e21, torre_de_cali, versalles, 1.6).
tramo(e21, versalles, las_americas, 0.8).
tramo(e21, las_americas, prados_del_norte, 3.5).
tramo(e21, prados_del_norte, vipasa, 1.3).
tramo(e21, vipasa, alamos, 1.9).
tramo(e21, alamos, menga, 2.3).
% E37
tramo(e37, paso_del_comercio, flora_industrial, 5.0).
tramo(e37, flora_industrial, salomia, 1.8).
tramo(e37, salomia, manzanares, 2.8).
tramo(e37, manzanares, torre_de_cali, 5.6).
tramo(e37, torre_de_cali, san_pedro, 0.8).
tramo(e37, san_pedro, petecuy, 1.6).
tramo(e37, petecuy, san_bosco, 3.6).
tramo(e37, san_bosco, santa_librada, 1.5).
tramo(e37, santa_librada, estadio, 2.8).
tramo(e37, estadio, tequendama, 2.4).
tramo(e37, tequendama, unidad_deportiva, 2.5).
tramo(e37, unidad_deportiva, tequendama, 3.0).
tramo(e37, tequendama, estadio, 2.4).
tramo(e37, estadio, santa_librada, 2.8).
tramo(e37, santa_librada, san_bosco, 1.5).
tramo(e37, san_bosco, centro, 2.8).
tramo(e37, centro, la_ermita, 1.5).
tramo(e37, la_ermita, torre_de_cali, 0.9).
tramo(e37, torre_de_cali, manzanares, 6.0).
tramo(e37, manzanares, salomia, 2.8).
tramo(e37, salomia, flora_industrial, 1.8).
tramo(e37, flora_industrial, chiminangos, 1.4).
tramo(e37, chiminangos, paso_del_comercio, 3.2).

% ---------------------------------------------------------------------
% REGLAS (conocimiento derivado)
% ---------------------------------------------------------------------

% R1. Un bus conecta A con B si recorre el tramo en ese sentido.
conecta(R, A, B, T) :- tramo(R, A, B, T).

% R2. Una ruta sirve a una estación si alguno de sus tramos sale de ella.
sirve(R, E) :- conecta(R, E, _, _).

% R3. Un tramo está disponible si ninguna de sus estaciones está cerrada
%     y la ruta no está suspendida (hechos que se agregan en tiempo de ejecución).
disponible(R, A, B, T) :- conecta(R, A, B, T), \+ cerrada(A), \+ cerrada(B), \+ suspendida(R).

% R4. Si una estación B está cerrada, el bus pasa sin detenerse:
%     el tramo A -> C queda disponible con la suma de los tiempos.
disponible(R, A, C, T) :- conecta(R, A, B, T1), cerrada(B), conecta(R, B, C, T2), distinto(A, C), \+ cerrada(A), \+ cerrada(C), \+ suspendida(R), suma(T1, T2, T).

% R5. Una ruta está operando en una estación si tiene tramos disponibles desde ella.
opera_en(R, E) :- disponible(R, E, _, _).

% R6. Hay transbordo en E entre R1 y R2 si ambas rutas operan allí.
transbordo(E, R1, R2) :- opera_en(R1, E), opera_en(R2, E), distinto(R1, R2).

% R7. Una estación de transbordo es la que tiene al menos un transbordo.
estacion_transbordo(E) :- transbordo(E, _, _).

% R8-R9. Costo (min) de cambiar de bus: menor en terminales.
costo_transbordo(E, 3) :- estacion_transbordo(E), terminal(E).
costo_transbordo(E, 5) :- estacion_transbordo(E), \+ terminal(E).

% R10. Espera promedio al abordar = la mitad de la frecuencia de la ruta.
espera(R, W) :- frecuencia(R, F), mitad(F, W).

% R11. Dos estaciones son vecinas si una ruta disponible va de una a la otra.
vecinas(A, B) :- disponible(_, A, B, _).

% R12-R13. Alcanzabilidad (regla recursiva): B es alcanzable desde A.
alcanzable(A, B) :- vecinas(A, B).
alcanzable(A, C) :- vecinas(A, B), alcanzable(B, C).
