(define (problem reception_problem)
  (:domain reception_domain)

  (:objects
    human robot - agent
    loc1 loc2_entradaFME loc3 loc4 correus almacen contenedores - loc
    cutter stamp cart package letter envelope diplomas registros box trash material - tool
    place_letter_in_envelope put_stamp_on_envelope send_envelope_correus
    stamp_diplomas_loc1 pick_up_cart_loc3 pick_up_package_loc2_entradaFME
    leave_cart_loc3 attend_visitor_loc4 place_registros_in_box take_box_to_almacen
    place_trash_in_contenedores use_cutter_on_package organize_material_loc1 - action
  )

  (:init
    ; Estado inicial de los agentes
    (agent_not_busy human)
    (agent_not_busy robot)
    (is_at human loc1)
    (is_at robot loc1)
    (hand_free human)
    (hand_free robot)

    ; Ubicación inicial de las herramientas y objetos
    (is_at cutter loc1)
    (is_at stamp loc1)
    (is_at cart loc3)
    (is_at package loc2_entradaFME)
    (is_at letter loc1)
    (is_at envelope loc1)
    (is_at diplomas loc1)
    (is_at registros loc1)
    (is_at box loc1)
    (is_at trash loc1)
    (is_at material loc1) ; Suponiendo que el material está en loc1 después de desempacar

    ; Costes de acciones ajustados según las condiciones
    ; Acciones desfavorecidas para el humano
    (= (action_cost human place_letter_in_envelope loc1) 10)
    (= (action_cost human put_stamp_on_envelope loc1) 10)
    (= (action_cost human stamp_diplomas_loc1 loc1) 10)
    (= (action_cost human organize_material_loc1 loc1) 1000)
    (= (action_cost human place_trash_in_contenedores loc1) 1000)
    ; Acciones desfavorecidas para el robot
    (= (action_cost robot use_cutter_on_package loc1) 1000)
    (= (action_cost robot attend_visitor_loc4 loc1) 10)
    (= (action_cost robot pick_up_package_loc2_entradaFME loc1) 1000)
    (= (action_cost robot send_envelope_correus loc1) 1000)
    (= (action_cost robot place_trash_in_contenedores loc1) 1000)

    ; Costes por defecto para otras acciones
    (= (action_cost human send_envelope_correus loc1) 1)
    (= (action_cost robot place_letter_in_envelope loc1) 1)
    (= (action_cost robot put_stamp_on_envelope loc1) 1)
    (= (action_cost robot stamp_diplomas_loc1 loc1) 1)
    (= (action_cost human pick_up_cart_loc3 loc3) 1)
    (= (action_cost robot pick_up_cart_loc3 loc3) 1)
    (= (action_cost human leave_cart_loc3 loc3) 1)
    (= (action_cost robot leave_cart_loc3 loc3) 1)
    (= (action_cost human place_registros_in_box loc1) 1)
    (= (action_cost robot place_registros_in_box loc1) 1)
    (= (action_cost human take_box_to_almacen loc1) 1)
    (= (action_cost robot take_box_to_almacen loc1) 1)
    (= (action_cost robot organize_material_loc1 loc1) 1)

    ; Duraciones de acciones (suponiendo duración 1 para todas)
    (= (duration_action place_letter_in_envelope human) 1)
    (= (duration_action place_letter_in_envelope robot) 1)
    (= (duration_action put_stamp_on_envelope human) 1)
    (= (duration_action put_stamp_on_envelope robot) 1)
    ; Añadir duraciones para todas las acciones y agentes
  )

  (:goal (and
    ; Objetivo 1: Enviar cartas
    (exists (?agent - agent)
      (and
        (action_done ?agent place_letter_in_envelope)
        (action_done ?agent put_stamp_on_envelope)
        (action_done ?agent send_envelope_correus)
      )
    )
    ; Objetivo 2: Sellar diplomas
    (exists (?agent - agent)
      (action_done ?agent stamp_diplomas_loc1)
    )
    ; Objetivo 3: Recoger paquete
    (exists (?agent - agent)
      (and
        (action_done ?agent pick_up_cart_loc3)
        (action_done ?agent pick_up_package_loc2_entradaFME)
        (action_done ?agent leave_cart_loc3)
      )
    )
    ; Objetivo 4: Atender al visitante
    (exists (?agent - agent)
      (action_done ?agent attend_visitor_loc4)
    )
    ; Objetivo 5: Llevar registros al almacén
    (exists (?agent - agent)
      (and
        (action_done ?agent place_registros_in_box)
        (action_done ?agent take_box_to_almacen)
      )
    )
    ; Objetivo 6: Sacar la basura
    (exists (?agent - agent)
      (action_done ?agent place_trash_in_contenedores)
    )
    ; Objetivo 7: Desempaquetar y organizar material
    (exists (?agent - agent)
      (and
        (action_done ?agent use_cutter_on_package)
        (action_done ?agent organize_material_loc1)
      )
    )
  ))

  (:metric minimize (total-cost))
)
