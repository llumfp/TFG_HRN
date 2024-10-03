(define (problem kitchen_collab_problem)
(:domain kitchen_collab_domain)

(:objects
    human robot - agent
    ; from environment
    ; ... - obj
    ; ... - loc
    table drawer bin floor - loc
    spoon napkin banana mop - obj
)

(:init
    (agent_not_busy robot)
    (agent_not_busy human)
    (=(used_to_clean_cost human mop floor) 50)
    (=(stored_cost robot spoon drawer) 50)
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
    (used_to_clean mop floor)
    (stored spoon drawer)
))
(:metric minimize (+ (* 1 (total-cost))(* 1 (total-time))))
)
