(define (problem problem_basic_duration)
(:domain domain_basic_duration)

(:objects
    human robot - agent
    loc1 loc2_entradaFME loc4 - loc
    paquete__recogido__loc2_entradaFME visitante__atendido__loc4 basura__colocada__contenedores diplomas__sellados__loc1 - action
)

(:init
    (agent_not_busy robot)
    (agent_not_busy human)

    (is_at human loc1)
    (is_at robot loc2)

    (action_loc paquete__recogido__loc2_entradaFME loc2_entradaFME)
    (action_end_loc paquete__recogido__loc2_entradaFME loc1)
    (action_loc visitante__atendido__loc4 loc4)
    (action_end_loc visitante__atendido__loc4 loc4)
    (action_loc basura__colocada__contenedores loc4)
    (action_end_loc basura__colocada__contenedores loc4)
    (action_loc diplomas__sellados__loc1 loc1)
    (action_end_loc diplomas__sellados__loc1 loc1)

    (=(action_duration human paquete__recogido__loc2_entradaFME) 20)
    (=(action_duration human visitante__atendido__loc4) 15)
    (=(action_duration human basura__colocada__contenedores) 15)
    (=(action_duration human diplomas__sellados__loc1) 15)
    (=(action_duration robot paquete__recogido__loc2_entradaFME) 10)
    (=(action_duration robot visitante__atendido__loc4) 15)
    (=(action_duration robot basura__colocada__contenedores) 20)
    (=(action_duration robot diplomas__sellados__loc1) 10)

    (=(action_cost human paquete__recogido__loc2_entradaFME) 0)
    (=(action_cost human visitante__atendido__loc4) 0)
    (=(action_cost human basura__colocada__contenedores) 0)
    (=(action_cost human diplomas__sellados__loc1) 20)
    (=(action_cost robot paquete__recogido__loc2_entradaFME) 0)
    (=(action_cost robot visitante__atendido__loc4) 20)
    (=(action_cost robot basura__colocada__contenedores) 20)
    (=(action_cost robot diplomas__sellados__loc1) 20)

    (= (total-cost robot) 0)
    (= (total-cost human) 0)
)
(:goal (and
    (action_done paquete__recogido__loc2_entradaFME)
    (action_done visitante__atendido__loc4)
    (action_done basura__colocada__contenedores)
    (action_done diplomas__sellados__loc1)
    ))
(:metric minimize (+ (* 1 (total-cost robot)) (* 1 (total-cost human)) (* 1 (total-time))))
)
