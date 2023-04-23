import random
import psycopg2
import math

#####CONNECTION TO DATABASE###################
conn = psycopg2.connect("dbname=pro_log user=postgres password=")
cursor = conn.cursor()

postgreSQL_select_Query_PROVEEDOR_DEMANDA = "select p_key,d_key,costo_pd,carga_sij_pd from proveedor_demanda"
cursor.execute(postgreSQL_select_Query_PROVEEDOR_DEMANDA)
proveedor_demanda_records = cursor.fetchall()

postgreSQL_select_Query_CROSSDOCK = "select ubicacion from crossdock"
cursor.execute(postgreSQL_select_Query_CROSSDOCK)
crossdock_records = cursor.fetchall()
#########################################################

################SUPUESTOS###############################

######Supuesto carga camion Homogenia/assumptions

Carga_Camion=30

Costo_Total_ganador=math.inf
Numero_de_simulaciones=10000
Temperatura=1000000000
cooler=0.9999
Dic_asignacion_crossdock_a_proveedor_ganador = {}
Dic_suma_de_demandas_para_cada_proveedor_crossdock_ganador={}
Dic_suma_de_proveedores_para_cada_crossdock_demanda_ganador={}
Dic_suma_de_proveedores_para_cada_proveedor_demanda_ganador={}


Dic_asignacion_crossdock_a_proveedor = {}
for row in proveedor_demanda_records:
        Dic_asignacion_crossdock_a_proveedor[(row[0]+"-"+row[1])]=[row[0],row[1],random.choice((1,0)),row[2],row[3]]
                

for i in range(Numero_de_simulaciones):
        #si es 1 , va directo de proveedor a demanda, 0 si no
        
        
        Dic_suma_de_demandas_para_cada_proveedor_crossdock={}
        Dic_suma_de_proveedores_para_cada_crossdock_demanda={}
        Dic_suma_de_proveedores_para_cada_proveedor_demanda={}


        #obtener las id de los crossdock para luego asignalar
        id_crossdock=[]
        for row in crossdock_records:
                id_crossdock.append(row[0])

        #asignar a aquellos que corresponda un crossdock

        for llave_valor in Dic_asignacion_crossdock_a_proveedor.items():
                #print(Dic_asignacion_crossdock_a_proveedor)
                if llave_valor[1][2] == 0:
                        
                        nuevo_valor=[llave_valor[1][0],llave_valor[1][1],llave_valor[1][2],llave_valor[1][3],llave_valor[1][4]]
                        nuevo_valor.append(random.choice((crossdock_records))[0])
                        p_key=nuevo_valor[0]
                        c_key=nuevo_valor[5]
                        d_key=nuevo_valor[1]
                        #########################################################
                        postgreSQL_select_Query_PROVEEDOR_CROSSDOCK = ("""
                                                                select "costo_pc"
                                                                from proveedor_crossdock 
                                                                where 
                                                                "p_key"::varchar = '{}'::varchar
                                                                AND
                                                                "c_key"::varchar = '{}'::varchar;
                                                                """).format(p_key,c_key)
                        cursor.execute(postgreSQL_select_Query_PROVEEDOR_CROSSDOCK)
                        proveedor_crossdock_records = cursor.fetchall()
                        nuevo_valor.append(proveedor_crossdock_records[0][0])
                        #########################################################
                        postgreSQL_select_Query_CROSSDOCK_DEMANDA = ("""
                                                                select "costo_cd"
                                                                from crossdock_demanda 
                                                                where 
                                                                "c_key"::varchar = '{}'::varchar
                                                                AND
                                                                "d_key"::varchar = '{}'::varchar;
                                                                """).format(c_key,d_key)
                        cursor.execute(postgreSQL_select_Query_CROSSDOCK_DEMANDA)
                        crossdock_demanda_records = cursor.fetchall()
                        nuevo_valor.append(crossdock_demanda_records[0][0])          
                        Dic_asignacion_crossdock_a_proveedor[llave_valor[0]]=nuevo_valor
                        
                        llave_plata_camion_proveedor_crossdock=nuevo_valor[0]+'-'+nuevo_valor[5]
                        llave_plata_camion_crossdock_demanda=nuevo_valor[5]+'-'+nuevo_valor[1]
                        
                        if llave_plata_camion_proveedor_crossdock in Dic_suma_de_demandas_para_cada_proveedor_crossdock.keys():
                                
                                llave_de_paso=Dic_suma_de_demandas_para_cada_proveedor_crossdock[llave_plata_camion_proveedor_crossdock]
                                carga=llave_de_paso[0]
                                carga+=nuevo_valor[4]
                                Dic_suma_de_demandas_para_cada_proveedor_crossdock[llave_plata_camion_proveedor_crossdock]=[carga,nuevo_valor[6]]
                                

                        else:
                                
                                Dic_suma_de_demandas_para_cada_proveedor_crossdock[llave_plata_camion_proveedor_crossdock]=[nuevo_valor[4],nuevo_valor[6]]
                        
                        
                        if llave_plata_camion_crossdock_demanda in Dic_suma_de_proveedores_para_cada_crossdock_demanda.keys():
                                
                                llave_de_paso=Dic_suma_de_proveedores_para_cada_crossdock_demanda[llave_plata_camion_crossdock_demanda]
                                carga=llave_de_paso[0]
                                carga+=nuevo_valor[4]
                                Dic_suma_de_proveedores_para_cada_crossdock_demanda[llave_plata_camion_crossdock_demanda]=[carga,nuevo_valor[7]]                       
                        else:       
                                Dic_suma_de_proveedores_para_cada_crossdock_demanda[llave_plata_camion_crossdock_demanda]=[nuevo_valor[4],nuevo_valor[7]]
                                
                        ########################################################################
                else:       
                        nuevo_valor=[llave_valor[1][0],llave_valor[1][1],llave_valor[1][2],llave_valor[1][3],llave_valor[1][4]]
                        nuevo_valor.append("DIRECTO")
                        nuevo_valor.append(0)
                        nuevo_valor.append(0)
                        Dic_asignacion_crossdock_a_proveedor[llave_valor[0]]=nuevo_valor
                        
                        llave_plata_camion_proveedor_demanda=nuevo_valor[0]+'-'+nuevo_valor[1]
                        Dic_suma_de_proveedores_para_cada_proveedor_demanda[llave_plata_camion_proveedor_demanda]=[nuevo_valor[4],nuevo_valor[3]]
                        
        Costo_Total=0
        #es carga,precio
        for i,x in Dic_suma_de_demandas_para_cada_proveedor_crossdock.items():
                alfa=[math.ceil((x[0]/Carga_Camion)),x[1]]
                Dic_suma_de_demandas_para_cada_proveedor_crossdock[i]=alfa
                
        for i,x in Dic_suma_de_proveedores_para_cada_crossdock_demanda.items():
                alfa=[math.ceil((x[0]/Carga_Camion)),x[1]]
                Dic_suma_de_proveedores_para_cada_crossdock_demanda[i]=alfa
                
        for i,x in Dic_suma_de_proveedores_para_cada_proveedor_demanda.items():
                alfa=[math.ceil((x[0]/Carga_Camion)),x[1]]
                Dic_suma_de_proveedores_para_cada_proveedor_demanda[i]=alfa
                
        
        for proveedor_crossdock in Dic_suma_de_demandas_para_cada_proveedor_crossdock.values():
                #print((math.ceil(proveedor_crossdock[0]/Carga_Camion)))
                #print(proveedor_crossdock[1])
                Costo_Total+=((proveedor_crossdock[0]))*proveedor_crossdock[1]
                
                
        for crossdock_demanda in Dic_suma_de_proveedores_para_cada_crossdock_demanda.values():
                #print((math.ceil(crossdock_demanda[0]/Carga_Camion)))
                #print(crossdock_demanda[1])
                Costo_Total+=((crossdock_demanda[0]))*crossdock_demanda[1]
                
        for proveedor_demanda in Dic_suma_de_proveedores_para_cada_proveedor_demanda.values():
                #print((math.ceil(proveedor_demanda[0]/Carga_Camion)))
                #print(proveedor_demanda[1])
                Costo_Total+=((proveedor_demanda[0]))*proveedor_demanda[1]

        
   


        if Costo_Total < Costo_Total_ganador:
                
                Costo_Total_ganador=Costo_Total
                Dic_asignacion_crossdock_a_proveedor_ganador=Dic_asignacion_crossdock_a_proveedor

                Dic_suma_de_demandas_para_cada_proveedor_crossdock_ganador=Dic_suma_de_demandas_para_cada_proveedor_crossdock
                Dic_suma_de_proveedores_para_cada_crossdock_demanda_ganador=Dic_suma_de_proveedores_para_cada_crossdock_demanda
                Dic_suma_de_proveedores_para_cada_proveedor_demanda_ganador=Dic_suma_de_proveedores_para_cada_proveedor_demanda

        else:
                delta=Costo_Total-Costo_Total_ganador

                if math.exp(-1*delta/Temperatura) > random.uniform(0,1):
                        Dic_asignacion_crossdock_a_proveedor = {}
                        for row in proveedor_demanda_records:
                                Dic_asignacion_crossdock_a_proveedor[(row[0]+"-"+row[1])]=[row[0],row[1],random.choice((1,0)),row[2],row[3]]
 
                Temperatura*=cooler

L=["Asiprintgnación de proveedores/demandas: \n \n"]

for vector in Dic_asignacion_crossdock_a_proveedor_ganador.values():    
        L.append("La demanda desde el proveedor {} hasta el nodo de demanda {} va vía {} \n".format(vector[0],vector[1],vector[5]))
L.append("\n \nAsignación de camiones: \n \n")
       
for proveedor_crossdock in Dic_suma_de_demandas_para_cada_proveedor_crossdock_ganador.items():
        L.append("Para el trayecto {} se requeriran {} camiones \n".format (proveedor_crossdock[0],(proveedor_crossdock[1][0])))   
L.append("\n")

for crossdock_demanda in Dic_suma_de_proveedores_para_cada_crossdock_demanda_ganador.items():
        L.append("Para el trayecto {} se requeriran {} camiones \n".format (crossdock_demanda[0],(crossdock_demanda[1][0])))    
L.append("\n")

for proveedor_demanda in Dic_suma_de_proveedores_para_cada_proveedor_demanda_ganador.items():
        L.append("Para el trayecto {} se requeriran {} camiones \n".format (proveedor_demanda[0],(proveedor_demanda[1][0])))
L.append("\n \nCosto del Plan: {} \n \n".format(Costo_Total_ganador)) 
  
plan_peranciones = open("Plan_Operaciones.txt","w")
plan_peranciones.writelines(L)
plan_peranciones.close()

                

       
        
        