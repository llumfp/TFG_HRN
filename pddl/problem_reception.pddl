(define (problem reception_problem)
(:domain reception_domain)

(:objects
    human robot - agent
    ; from environment
    ; ... - obj
    ; ... - loc
    table1 table2 - loc
    pen documents paper - obj
)

(:init
    (agent_not_busy robot)
    (agent_not_busy human)
    (=(stamp_cost human paper table2) 50)
    (=(put_cost robot documents table1) 50)
    (=(put_cost human documents table1) 35)
    (=(pick_up_cost human pen table1) 25)
    ; action costs from llm based on agent states and preferences

    (= (total-cost) 0)

    ; (=(used_to_clean_cost human mop floor) -50)
    ; (=(stored_cost robot spoon drawer) 100)
    ; ; action costs from llm based on agent states and preferences

    ; (= (total-cost) 200)

)

(:goal (and
    ; goals from llm based on environment
    ; (stored napkin bin)
    ; (served_as_snack banana table)
    (is_into_box documents table1)
    (stamped paper table2)
    (picked_up pen table1)
))
(:metric minimize (+ (* 1 (total-cost))(* 1 (total-time))))
)
