(define (problem problem_simple)
(:domain domain_simple)

(:objects
    human robot - agent
    loc1 loc2 - loc
    stamp_diplomas - static_action
    recieve_package - dynamic_action
)

(:init
    (agent_not_busy robot)
    (agent_not_busy human)
    (is_at human loc1)
    (is_at robot loc2)
    (action_loc stamp_diplomas loc1)
    (action_loc recieve_package loc2)
    (action_end_loc recieve_package loc1)
    (=(action_cost human stamp_diplomas) 50)
    (=(action_cost robot stamp_diplomas) 25)
    (=(action_cost human recieve_package) 100)
    (=(action_cost robot recieve_package) 100)
    (= (total-cost) 0)
)

(:goal (and
    (action_executed stamp_diplomas)
    (action_executed recieve_package)
    ))
(:metric minimize (+ (* 1 (total-cost))(* 1 (total-time))))
)
